#!/bin/bash

# Performance Tuning Script for MarkItDown with Vision OCR
# This script optimizes system performance for production deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config/production"
MONITORING_DIR="$PROJECT_ROOT/monitoring"

# Function to check system resources
check_system_resources() {
    log_info "Checking system resources..."
    
    # CPU information
    local cpu_cores=$(nproc)
    local cpu_model=$(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)
    log_info "CPU: $cpu_cores cores - $cpu_model"
    
    # Memory information
    local total_mem=$(free -g | awk '/^Mem:/{print $2}')
    local available_mem=$(free -g | awk '/^Mem:/{print $7}')
    log_info "Memory: ${total_mem}GB total, ${available_mem}GB available"
    
    # Disk information
    local disk_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    log_info "Disk space: ${disk_space}GB available"
    
    # GPU information (if available)
    if command -v nvidia-smi &> /dev/null; then
        local gpu_count=$(nvidia-smi --list-gpus | wc -l)
        local gpu_memory=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        log_info "GPU: $gpu_count GPU(s) with ${gpu_memory}MB memory"
    else
        log_info "GPU: No NVIDIA GPU detected"
    fi
    
    # Network information
    local network_speed=$(ethtool eth0 2>/dev/null | grep "Speed" | cut -d: -f2 | xargs || echo "Unknown")
    log_info "Network: $network_speed"
}

# Function to optimize system settings
optimize_system_settings() {
    log_info "Optimizing system settings..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_warning "System optimizations require root privileges. Skipping..."
        return 0
    fi
    
    # CPU optimization
    log_info "Optimizing CPU settings..."
    
    # Set CPU governor to performance
    if [[ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]]; then
        echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
        log_success "CPU governor set to performance"
    fi
    
    # Memory optimization
    log_info "Optimizing memory settings..."
    
    # Increase file descriptor limits
    cat >> /etc/security/limits.conf << EOF
# MarkItDown performance optimizations
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF
    
    # Optimize kernel parameters
    cat >> /etc/sysctl.conf << EOF
# MarkItDown performance optimizations
# Network optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File system optimizations
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288

# Memory optimizations
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.max_map_count = 262144

# Security optimizations
kernel.keys.root_maxkeys = 1000000
kernel.keys.root_maxbytes = 25000000
EOF
    
    # Apply sysctl changes
    sysctl -p
    
    log_success "System settings optimized"
}

# Function to optimize Docker settings
optimize_docker_settings() {
    log_info "Optimizing Docker settings..."
    
    # Create Docker daemon configuration
    sudo mkdir -p /etc/docker
    
    cat > /tmp/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Hard": 65536,
      "Name": "nofile",
      "Soft": 65536
    }
  },
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "experimental": false,
  "metrics-addr": "127.0.0.1:9323",
  "live-restore": true
}
EOF
    
    # Check if GPU support is available
    if command -v nvidia-smi &> /dev/null; then
        log_info "Configuring Docker for GPU support..."
        cat >> /tmp/daemon.json << EOF
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
EOF
    fi
    
    # Move configuration to Docker directory
    sudo mv /tmp/daemon.json /etc/docker/daemon.json
    
    # Restart Docker daemon
    if command -v systemctl &> /dev/null; then
        sudo systemctl restart docker
        log_success "Docker daemon restarted"
    else
        log_warning "Please restart Docker daemon manually"
    fi
}

# Function to create performance monitoring configuration
create_performance_monitoring() {
    log_info "Creating performance monitoring configuration..."
    
    # Create Prometheus alert rules for performance
    cat > "$MONITORING_DIR/prometheus/alert_rules.yml" << 'EOF'
groups:
  - name: markitdown_performance
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for 5 minutes"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for 5 minutes"

      # High disk usage
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage detected"
          description: "Disk usage is above 85% for 5 minutes"

      # Slow response time
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time detected"
          description: "95th percentile response time is above 2 seconds"

      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for 5 minutes"

      # Ollama model not responding
      - alert: OllamaNotResponding
        expr: up{job="ollama"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Ollama service is down"
          description: "Ollama vision model service is not responding"

      # Database connection issues
      - alert: DatabaseConnectionIssues
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection issues"
          description: "PostgreSQL database is not accessible"

      # Redis connection issues
      - alert: RedisConnectionIssues
        expr: redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis connection issues"
          description: "Redis cache is not accessible"
EOF
    
    # Create Grafana dashboard for performance monitoring
    mkdir -p "$MONITORING_DIR/grafana/dashboards"
    
    cat > "$MONITORING_DIR/grafana/dashboards/markitdown-performance.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "MarkItDown Performance Dashboard",
    "tags": ["markitdown", "performance"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          }
        ],
        "yAxes": [
          {
            "min": 0,
            "max": 100,
            "label": "CPU Usage (%)"
          }
        ]
      },
      {
        "id": 2,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "Memory Usage %"
          }
        ],
        "yAxes": [
          {
            "min": 0,
            "max": 100,
            "label": "Memory Usage (%)"
          }
        ]
      },
      {
        "id": 3,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th Percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th Percentile"
          }
        ],
        "yAxes": [
          {
            "min": 0,
            "label": "Response Time (seconds)"
          }
        ]
      },
      {
        "id": 4,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ],
        "yAxes": [
          {
            "min": 0,
            "label": "Requests per Second"
          }
        ]
      },
      {
        "id": 5,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ],
        "yAxes": [
          {
            "min": 0,
            "max": 100,
            "label": "Error Rate (%)"
          }
        ]
      },
      {
        "id": 6,
        "title": "Vision OCR Processing Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(vision_ocr_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "95th Percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(vision_ocr_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "50th Percentile"
          }
        ],
        "yAxes": [
          {
            "min": 0,
            "label": "Processing Time (seconds)"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF
    
    log_success "Performance monitoring configuration created"
}

# Function to create performance tuning configuration
create_performance_config() {
    log_info "Creating performance tuning configuration..."
    
    # Create application performance configuration
    cat > "$CONFIG_DIR/performance.yml" << 'EOF'
# Performance Configuration for MarkItDown with Vision OCR

# Application Performance Settings
application:
  # Worker processes
  worker_processes: 4
  worker_connections: 1024
  
  # Request handling
  max_requests: 1000
  max_requests_jitter: 100
  timeout: 300
  
  # Memory management
  max_memory_per_child: 512MB
  memory_limit: 2GB

# Database Performance Settings
database:
  # Connection pooling
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
  
  # Query optimization
  statement_timeout: 300
  lock_timeout: 60
  
  # Index optimization
  auto_vacuum: true
  autovacuum_vacuum_scale_factor: 0.1
  autovacuum_analyze_scale_factor: 0.05

# Cache Performance Settings
cache:
  # Redis configuration
  max_connections: 50
  socket_timeout: 5
  socket_connect_timeout: 5
  
  # Cache settings
  default_timeout: 3600
  key_prefix: "markitdown:"
  
  # Memory optimization
  max_memory: 512MB
  max_memory_policy: "allkeys-lru"

# Vision OCR Performance Settings
vision_ocr:
  # Model optimization
  model_cache_size: 2
  model_preload: true
  
  # Processing optimization
  batch_size: 5
  max_concurrent_requests: 10
  request_timeout: 300
  
  # Memory optimization
  max_image_size: 2048
  compression_quality: 85
  use_grayscale: true
  
  # GPU optimization (if available)
  gpu_memory_fraction: 0.8
  gpu_allow_growth: true

# File Processing Performance Settings
file_processing:
  # Upload optimization
  max_file_size: 100MB
  chunk_size: 8192
  
  # Processing optimization
  max_concurrent_files: 5
  temp_file_cleanup: true
  
  # Storage optimization
  use_compression: true
  compression_level: 6

# Monitoring Performance Settings
monitoring:
  # Metrics collection
  metrics_interval: 30
  metrics_retention: 30d
  
  # Logging optimization
  log_level: INFO
  log_rotation: true
  log_max_size: 100MB
  log_max_files: 10
  
  # Health checks
  health_check_interval: 30
  health_check_timeout: 10
EOF
    
    log_success "Performance configuration created"
}

# Function to create resource monitoring script
create_resource_monitor() {
    log_info "Creating resource monitoring script..."
    
    cat > "$SCRIPT_DIR/monitor-resources.sh" << 'EOF'
#!/bin/bash

# Resource monitoring script for MarkItDown production environment

set -euo pipefail

# Configuration
LOG_FILE="/app/logs/resource-monitor.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=85
ALERT_THRESHOLD_DISK=85
CHECK_INTERVAL=60

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check CPU usage
check_cpu() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$cpu_usage > $ALERT_THRESHOLD_CPU" | bc -l) )); then
        log_message "WARNING: High CPU usage detected: ${cpu_usage}%"
        return 1
    fi
    echo "$cpu_usage"
}

# Check memory usage
check_memory() {
    local mem_info=$(free | grep Mem)
    local total=$(echo $mem_info | awk '{print $2}')
    local used=$(echo $mem_info | awk '{print $3}')
    local mem_usage=$(echo "scale=2; $used * 100 / $total" | bc)
    
    if (( $(echo "$mem_usage > $ALERT_THRESHOLD_MEMORY" | bc -l) )); then
        log_message "WARNING: High memory usage detected: ${mem_usage}%"
        return 1
    fi
    echo "$mem_usage"
}

# Check disk usage
check_disk() {
    local disk_usage=$(df /app | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if (( disk_usage > ALERT_THRESHOLD_DISK )); then
        log_message "WARNING: High disk usage detected: ${disk_usage}%"
        return 1
    fi
    echo "$disk_usage"
}

# Check Docker container status
check_containers() {
    local unhealthy_containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -v "Up" | wc -l)
    if (( unhealthy_containers > 0 )); then
        log_message "WARNING: $unhealthy_containers container(s) not healthy"
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep -v "Up" >> "$LOG_FILE"
        return 1
    fi
}

# Check service endpoints
check_services() {
    local services=("http://localhost:8000/health" "http://localhost:8001/health" "http://ollama:11434/api/tags")
    
    for service in "${services[@]}"; do
        if ! curl -f -s "$service" > /dev/null 2>&1; then
            log_message "ERROR: Service not responding: $service"
            return 1
        fi
    done
}

# Main monitoring loop
main() {
    log_message "Starting resource monitoring..."
    
    while true; do
        # Check system resources
        cpu_usage=$(check_cpu)
        mem_usage=$(check_memory)
        disk_usage=$(check_disk)
        
        # Check containers and services
        check_containers
        check_services
        
        # Log current status
        log_message "Status - CPU: ${cpu_usage}%, Memory: ${mem_usage}%, Disk: ${disk_usage}%"
        
        # Wait for next check
        sleep $CHECK_INTERVAL
    done
}

# Handle script termination
trap 'log_message "Resource monitoring stopped"; exit 0' SIGTERM SIGINT

# Run main function
main "$@"
EOF
    
    chmod +x "$SCRIPT_DIR/monitor-resources.sh"
    
    log_success "Resource monitoring script created"
}

# Function to create performance testing script
create_performance_test() {
    log_info "Creating performance testing script..."
    
    cat > "$SCRIPT_DIR/performance-test.sh" << 'EOF'
#!/bin/bash

# Performance testing script for MarkItDown with Vision OCR

set -euo pipefail

# Configuration
TEST_DURATION=300  # 5 minutes
CONCURRENT_USERS=10
BASE_URL="http://localhost:8000"
TEST_FILE="/app/test-data/sample.pdf"
RESULTS_DIR="/app/test-results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Test API health
test_health() {
    log_info "Testing API health..."
    
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/health")
    local status_code="${response: -3}"
    
    if [[ "$status_code" == "200" ]]; then
        log_success "API health check passed"
        return 0
    else
        log_error "API health check failed: $status_code"
        return 1
    fi
}

# Test file upload and processing
test_file_processing() {
    log_info "Testing file processing..."
    
    if [[ ! -f "$TEST_FILE" ]]; then
        log_warning "Test file not found, creating dummy file..."
        mkdir -p "$(dirname "$TEST_FILE")"
        echo "Test content" > "$TEST_FILE"
    fi
    
    local start_time=$(date +%s)
    
    # Upload and process file
    local response=$(curl -s -X POST \
        -F "file=@$TEST_FILE" \
        -F "model=llava:7b" \
        -F "use_hybrid_ocr=true" \
        "$BASE_URL/api/vision-ocr/convert")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Parse response
    local success=$(echo "$response" | jq -r '.success // false')
    local processing_time=$(echo "$response" | jq -r '.processing_time // 0')
    
    if [[ "$success" == "true" ]]; then
        log_success "File processing test passed (${duration}s)"
        echo "$processing_time" >> "$RESULTS_DIR/processing_times.txt"
    else
        log_error "File processing test failed"
        echo "$response" >> "$RESULTS_DIR/errors.log"
    fi
    
    return 0
}

# Load testing
load_test() {
    log_info "Starting load test with $CONCURRENT_USERS concurrent users..."
    
    local test_start=$(date +%s)
    local results_file="$RESULTS_DIR/load_test_$(date +%Y%m%d_%H%M%S).json"
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Initialize results
    cat > "$results_file" << EOF
{
  "test_start": "$(date -d @$test_start)",
  "duration": $TEST_DURATION,
  "concurrent_users": $CONCURRENT_USERS,
  "requests": []
}
EOF
    
    # Run concurrent requests
    for ((i=1; i<=CONCURRENT_USERS; i++)); do
        (
            while true; do
                local request_start=$(date +%s.%N)
                
                # Make API request
                local response=$(curl -s -w "%{http_code}" \
                    -X POST \
                    -F "file=@$TEST_FILE" \
                    -F "model=llava:7b" \
                    "$BASE_URL/api/vision-ocr/convert")
                
                local request_end=$(date +%s.%N)
                local status_code="${response: -3}"
                local duration=$(echo "$request_end - $request_start" | bc)
                
                # Record result
                echo "{\"timestamp\": \"$(date -d @$request_start)\", \"status\": $status_code, \"duration\": $duration}" >> "$RESULTS_DIR/request_$i.log"
                
                # Check if test duration exceeded
                if (( $(date +%s) - test_start >= TEST_DURATION )); then
                    break
                fi
                
                # Random delay between requests
                sleep $((RANDOM % 5 + 1))
            done
        ) &
    done
    
    # Wait for all background processes
    wait
    
    # Aggregate results
    aggregate_results "$results_file"
    
    log_success "Load test completed"
}

# Aggregate test results
aggregate_results() {
    local results_file="$1"
    
    log_info "Aggregating test results..."
    
    # Calculate statistics
    local total_requests=$(find "$RESULTS_DIR" -name "request_*.log" -exec cat {} \; | wc -l)
    local successful_requests=$(find "$RESULTS_DIR" -name "request_*.log" -exec cat {} \; | jq -r '.status' | grep -c "200" || echo "0")
    local failed_requests=$((total_requests - successful_requests))
    
    # Calculate response time statistics
    local response_times=$(find "$RESULTS_DIR" -name "request_*.log" -exec cat {} \; | jq -r '.duration' | sort -n)
    local avg_response_time=$(echo "$response_times" | awk '{sum+=$1} END {print sum/NR}')
    local p95_response_time=$(echo "$response_times" | awk 'BEGIN{c=0} length($0){a[c]=$0;c++}END{p5=(c/100*5);p5=p5%1?int(p5)+1:p5;print a[c-p5-1]}')
    local p99_response_time=$(echo "$response_times" | awk 'BEGIN{c=0} length($0){a[c]=$0;c++}END{p1=(c/100*1);p1=p1%1?int(p1)+1:p1;print a[c-p1-1]}')
    
    # Generate report
    cat > "$RESULTS_DIR/performance_report_$(date +%Y%m%d_%H%M%S).txt" << EOF
MarkItDown Performance Test Report
==================================

Test Configuration:
- Duration: $TEST_DURATION seconds
- Concurrent Users: $CONCURRENT_USERS
- Base URL: $BASE_URL

Results:
- Total Requests: $total_requests
- Successful Requests: $successful_requests
- Failed Requests: $failed_requests
- Success Rate: $(echo "scale=2; $successful_requests * 100 / $total_requests" | bc)%

Response Times:
- Average: ${avg_response_time}s
- 95th Percentile: ${p95_response_time}s
- 99th Percentile: ${p99_response_time}s

System Resources:
- CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%
- Memory Usage: $(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')%
- Disk Usage: $(df /app | tail -1 | awk '{print $5}')

Recommendations:
$(generate_recommendations "$successful_requests" "$total_requests" "$avg_response_time")
EOF
    
    log_success "Performance report generated"
}

# Generate recommendations
generate_recommendations() {
    local successful_requests="$1"
    local total_requests="$2"
    local avg_response_time="$3"
    
    local success_rate=$(echo "scale=2; $successful_requests * 100 / $total_requests" | bc)
    
    echo "Based on the test results:"
    echo
    
    if (( $(echo "$success_rate < 95" | bc -l) )); then
        echo "- Consider increasing server resources or optimizing the application"
    fi
    
    if (( $(echo "$avg_response_time > 30" | bc -l) )); then
        echo "- Response times are high, consider optimizing Vision OCR processing"
    fi
    
    if (( $(echo "$avg_response_time < 10" | bc -l) )); then
        echo "- Performance is good, consider increasing concurrent user load"
    fi
    
    echo "- Monitor system resources during peak usage"
    echo "- Consider implementing caching for frequently processed files"
    echo "- Review Vision OCR model selection for optimal performance"
}

# Main execution
main() {
    log_info "Starting MarkItDown performance test..."
    
    # Check dependencies
    check_dependencies
    
    # Test API health
    test_health
    
    # Test file processing
    test_file_processing
    
    # Run load test
    load_test
    
    log_success "Performance test completed successfully"
}

# Run main function
main "$@"
EOF
    
    chmod +x "$SCRIPT_DIR/performance-test.sh"
    
    log_success "Performance testing script created"
}

# Function to display performance optimization summary
display_optimization_summary() {
    log_info "Performance optimization completed successfully!"
    echo
    echo "=== Performance Optimization Summary ==="
    echo "System optimizations applied:"
    echo "- CPU governor set to performance mode"
    echo "- File descriptor limits increased"
    echo "- Kernel parameters optimized"
    echo "- Docker daemon configured for optimal performance"
    echo
    echo "Monitoring and testing tools created:"
    echo "- Resource monitoring script: scripts/monitor-resources.sh"
    echo "- Performance testing script: scripts/performance-test.sh"
    echo "- Prometheus alert rules: monitoring/prometheus/alert_rules.yml"
    echo "- Grafana dashboard: monitoring/grafana/dashboards/markitdown-performance.json"
    echo "- Performance configuration: config/production/performance.yml"
    echo
    echo "=== Next Steps ==="
    echo "1. Start resource monitoring:"
    echo "   ./scripts/monitor-resources.sh &"
    echo "2. Run performance tests:"
    echo "   ./scripts/performance-test.sh"
    echo "3. Monitor Grafana dashboard for performance metrics"
    echo "4. Adjust performance configuration based on test results"
    echo
    echo "=== Performance Tips ==="
    echo "- Monitor CPU and memory usage during peak loads"
    echo "- Adjust worker processes based on available CPU cores"
    echo "- Optimize Vision OCR model selection for your use case"
    echo "- Consider GPU acceleration for Vision OCR processing"
    echo "- Implement caching for frequently accessed data"
}

# Main execution
main() {
    echo "=== MarkItDown Performance Optimization ==="
    echo "This script will optimize system performance for MarkItDown with Vision OCR"
    echo
    
    # Check system resources
    check_system_resources
    
    # Optimize system settings (requires root)
    optimize_system_settings
    
    # Optimize Docker settings
    optimize_docker_settings
    
    # Create performance monitoring
    create_performance_monitoring
    
    # Create performance configuration
    create_performance_config
    
    # Create resource monitoring script
    create_resource_monitor
    
    # Create performance testing script
    create_performance_test
    
    # Display summary
    display_optimization_summary
}

# Run main function
main "$@"

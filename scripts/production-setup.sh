#!/bin/bash

# Production Environment Setup Script for MarkItDown with Vision OCR
# This script prepares the production environment with security hardening,
# performance optimization, and monitoring setup.

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
ENV_FILE="$PROJECT_ROOT/.env.production"
CONFIG_DIR="$PROJECT_ROOT/config/production"
SECURITY_DIR="$PROJECT_ROOT/security"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOGS_DIR="$PROJECT_ROOT/logs"

# Function to check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_warning "This script is optimized for Linux. Other OS may have issues."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check available memory
    local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $mem_gb -lt 16 ]]; then
        log_warning "Recommended minimum 16GB RAM. Current: ${mem_gb}GB"
    fi
    
    # Check available disk space
    local disk_gb=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $disk_gb -lt 50 ]]; then
        log_warning "Recommended minimum 50GB free space. Current: ${disk_gb}GB"
    fi
    
    log_success "System requirements check completed"
}

# Function to generate secure passwords
generate_secure_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to create production environment file
create_production_env() {
    log_info "Creating production environment configuration..."
    
    if [[ -f "$ENV_FILE" ]]; then
        log_warning "Production environment file already exists. Backing up..."
        cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    cat > "$ENV_FILE" << EOF
# Production Environment Configuration for MarkItDown with Vision OCR
# Generated on $(date)

# Database Configuration
DB_PASSWORD=$(generate_secure_password)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=markitdown
DB_USER=markitdown

# Redis Configuration
REDIS_PASSWORD=$(generate_secure_password)
REDIS_HOST=redis
REDIS_PORT=6379

# Security Configuration
SECRET_KEY=$(generate_secure_password)
ALLOWED_HOSTS=localhost,127.0.0.1,*.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
VISION_OCR_MODEL=llava:7b
OLLAMA_TIMEOUT=300

# Application Configuration
NODE_ENV=production
DEBUG=false
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=100MB
FILE_UPLOAD_TIMEOUT=300

# Performance Configuration
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1024
KEEPALIVE_TIMEOUT=65
CLIENT_MAX_BODY_SIZE=100M

# Monitoring Configuration
GRAFANA_PASSWORD=$(generate_secure_password)
PROMETHEUS_RETENTION_DAYS=30
ELASTICSEARCH_HEAP_SIZE=1g

# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"

# SSL/TLS Configuration
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
SSL_DH_PARAM_PATH=/etc/nginx/ssl/dhparam.pem

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Cache Configuration
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Vision OCR Advanced Configuration
VISION_OCR_QUALITY_THRESHOLD=0.8
VISION_OCR_BATCH_SIZE=5
VISION_OCR_MAX_RETRIES=3
VISION_OCR_FALLBACK_ENABLED=true

# Logging Configuration
LOG_FORMAT=json
LOG_ROTATION_SIZE=100MB
LOG_ROTATION_COUNT=10

# Health Check Configuration
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3
EOF
    
    log_success "Production environment file created: $ENV_FILE"
}

# Function to create production configuration directories
create_production_config() {
    log_info "Creating production configuration directories..."
    
    # Create configuration directories
    mkdir -p "$CONFIG_DIR"/{nginx,ssl,security,monitoring}
    mkdir -p "$SECURITY_DIR"/{apparmor,firewall,ssl}
    mkdir -p "$MONITORING_DIR"/{prometheus,grafana,alertmanager,filebeat}
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOGS_DIR"/{nginx,application,security}
    
    # Create production nginx configuration
    cat > "$CONFIG_DIR/nginx/nginx.prod.conf" << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;" always;
    
    # Upstream servers
    upstream markitdown_web {
        server markitdown-web:8000 max_fails=3 fail_timeout=30s;
    }
    
    upstream markitdown_mcp {
        server markitdown-mcp:8001 max_fails=3 fail_timeout=30s;
    }
    
    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_dhparam /etc/nginx/ssl/dhparam.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://markitdown_web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # MCP endpoints
        location /mcp/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://markitdown_mcp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # Root location
        location / {
            proxy_pass http://markitdown_web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
    
    log_success "Production configuration directories created"
}

# Function to create security configurations
create_security_config() {
    log_info "Creating security configurations..."
    
    # Create AppArmor profile
    cat > "$SECURITY_DIR/apparmor/markitdown.profile" << 'EOF'
#include <tunables/global>

profile markitdown flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/python>
  
  # Application directories
  /app/** r,
  /app/data/uploads/** rw,
  /app/data/models/** r,
  /app/logs/** rw,
  /app/cache/** rw,
  
  # Network access
  network inet tcp,
  network inet udp,
  
  # Process management
  capability sys_ptrace,
  capability sys_admin,
  
  # File operations
  /proc/** r,
  /sys/** r,
  /tmp/** rw,
  /var/tmp/** rw,
  
  # Deny dangerous operations
  deny /proc/sys/** w,
  deny /sys/** w,
  deny /dev/** w,
  deny /boot/** w,
  deny /etc/** w,
  deny /root/** w,
  deny /home/** w,
}
EOF
    
    # Create firewall rules
    cat > "$SECURITY_DIR/firewall/iptables.rules" << 'EOF'
# MarkItDown Production Firewall Rules
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]

# Allow loopback
-A INPUT -i lo -j ACCEPT

# Allow established connections
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (adjust port as needed)
-A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
-A INPUT -p tcp --dport 80 -j ACCEPT
-A INPUT -p tcp --dport 443 -j ACCEPT

# Allow Docker internal communication
-A INPUT -s 172.20.0.0/16 -j ACCEPT

# Allow monitoring ports
-A INPUT -p tcp --dport 9090 -j ACCEPT  # Prometheus
-A INPUT -p tcp --dport 3000 -j ACCEPT  # Grafana
-A INPUT -p tcp --dport 5601 -j ACCEPT  # Kibana

# Drop everything else
-A INPUT -j DROP

COMMIT
EOF
    
    log_success "Security configurations created"
}

# Function to create monitoring configurations
create_monitoring_config() {
    log_info "Creating monitoring configurations..."
    
    # Create Prometheus configuration
    cat > "$MONITORING_DIR/prometheus/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'markitdown-web'
    static_configs:
      - targets: ['markitdown-web:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'markitdown-mcp'
    static_configs:
      - targets: ['markitdown-mcp:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
    metrics_path: '/api/metrics'
    scrape_interval: 60s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF
    
    # Create AlertManager configuration
    cat > "$MONITORING_DIR/alertmanager/alertmanager.yml" << 'EOF'
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF
    
    # Create Filebeat configuration
    cat > "$MONITORING_DIR/filebeat/filebeat.yml" << 'EOF'
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/markitdown/*.log
  json.keys_under_root: true
  json.add_error_key: true
  json.message_key: log

- type: docker
  enabled: true
  containers.ids:
    - "*"
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices:
    - index: "filebeat-%{[agent.version]}-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
EOF
    
    log_success "Monitoring configurations created"
}

# Function to create startup scripts
create_startup_scripts() {
    log_info "Creating startup scripts..."
    
    # Create production startup script
    cat > "$SCRIPT_DIR/start-production.sh" << 'EOF'
#!/bin/bash

# Production startup script for MarkItDown with Vision OCR

set -euo pipefail

# Load environment variables
if [[ -f /app/.env.production ]]; then
    export $(cat /app/.env.production | grep -v '^#' | xargs)
fi

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    
    echo "Waiting for $service to be ready..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service is ready"
}

# Wait for dependencies
wait_for_service postgres 5432 "PostgreSQL"
wait_for_service redis 6379 "Redis"
wait_for_service ollama 11434 "Ollama"

# Start services
echo "Starting MarkItDown services..."

# Start MCP server in background
python -m markitdown_mcp_server &
MCP_PID=$!

# Start Web UI
python -m markitdown_web_ui &
WEB_PID=$!

# Wait for processes
wait $MCP_PID $WEB_PID
EOF
    
    # Create health check script
    cat > "$SCRIPT_DIR/health-check.sh" << 'EOF'
#!/bin/bash

# Health check script for MarkItDown services

# Check Web UI
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Web UI health check failed"
    exit 1
fi

# Check MCP Server
if ! curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "MCP Server health check failed"
    exit 1
fi

# Check Ollama
if ! curl -f http://ollama:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama health check failed"
    exit 1
fi

echo "All services healthy"
exit 0
EOF
    
    # Make scripts executable
    chmod +x "$SCRIPT_DIR/start-production.sh"
    chmod +x "$SCRIPT_DIR/health-check.sh"
    
    log_success "Startup scripts created"
}

# Function to create backup script
create_backup_script() {
    log_info "Creating backup script..."
    
    cat > "$SCRIPT_DIR/backup.sh" << 'EOF'
#!/bin/bash

# Backup script for MarkItDown production data

set -euo pipefail

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="markitdown_backup_$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
pg_dump -h postgres -U markitdown -d markitdown > "$BACKUP_DIR/$BACKUP_NAME/database.sql"

# Backup uploaded files
echo "Backing up uploaded files..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME/uploads.tar.gz" -C /app/data uploads/

# Backup configuration files
echo "Backing up configuration files..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME/config.tar.gz" -C /app config/

# Create backup manifest
cat > "$BACKUP_DIR/$BACKUP_NAME/manifest.txt" << MANIFEST
Backup created: $(date)
Database: markitdown
Uploads: /app/data/uploads
Configuration: /app/config
Backup size: $(du -sh "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
MANIFEST

# Compress entire backup
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Clean old backups (keep last 30 days)
find "$BACKUP_DIR" -name "markitdown_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_NAME}.tar.gz"
EOF
    
    chmod +x "$SCRIPT_DIR/backup.sh"
    
    log_success "Backup script created"
}

# Function to perform security audit
perform_security_audit() {
    log_info "Performing security audit..."
    
    # Check for common security issues
    local issues=0
    
    # Check file permissions
    if [[ -f "$ENV_FILE" ]]; then
        if [[ $(stat -c %a "$ENV_FILE") != "600" ]]; then
            log_warning "Environment file should have 600 permissions"
            chmod 600 "$ENV_FILE"
            issues=$((issues + 1))
        fi
    fi
    
    # Check for default passwords
    if grep -q "password\|secret" "$ENV_FILE" 2>/dev/null; then
        if grep -q "changeme\|default\|admin" "$ENV_FILE" 2>/dev/null; then
            log_warning "Default passwords detected in environment file"
            issues=$((issues + 1))
        fi
    fi
    
    # Check Docker security
    if docker info 2>/dev/null | grep -q "rootless"; then
        log_success "Docker running in rootless mode"
    else
        log_warning "Consider running Docker in rootless mode for better security"
        issues=$((issues + 1))
    fi
    
    if [[ $issues -eq 0 ]]; then
        log_success "Security audit passed"
    else
        log_warning "Security audit found $issues issues"
    fi
}

# Function to validate configuration
validate_configuration() {
    log_info "Validating configuration..."
    
    # Check required environment variables
    local required_vars=("DB_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$ENV_FILE" 2>/dev/null; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Validate Docker Compose configuration
    if ! docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
        log_error "Invalid Docker Compose configuration"
        exit 1
    fi
    
    log_success "Configuration validation passed"
}

# Function to display setup summary
display_setup_summary() {
    log_info "Production setup completed successfully!"
    echo
    echo "=== Production Setup Summary ==="
    echo "Environment file: $ENV_FILE"
    echo "Configuration directory: $CONFIG_DIR"
    echo "Security directory: $SECURITY_DIR"
    echo "Monitoring directory: $MONITORING_DIR"
    echo "Backup directory: $BACKUP_DIR"
    echo "Logs directory: $LOGS_DIR"
    echo
    echo "=== Next Steps ==="
    echo "1. Review and customize the configuration files"
    echo "2. Update the environment file with your domain and settings"
    echo "3. Generate SSL certificates for HTTPS"
    echo "4. Start the production environment:"
    echo "   docker-compose -f docker-compose.prod.yml up -d"
    echo "5. Monitor the logs:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f"
    echo
    echo "=== Security Notes ==="
    echo "- Change all default passwords in the environment file"
    echo "- Configure firewall rules for your network"
    echo "- Set up SSL certificates for HTTPS"
    echo "- Regularly update dependencies and security patches"
    echo "- Monitor logs and alerts for security issues"
    echo
    echo "=== Monitoring Access ==="
    echo "Grafana: http://localhost:3000 (admin / password from env file)"
    echo "Prometheus: http://localhost:9090"
    echo "Kibana: http://localhost:5601"
    echo "AlertManager: http://localhost:9093"
}

# Main execution
main() {
    echo "=== MarkItDown Production Setup ==="
    echo "This script will prepare your production environment for MarkItDown with Vision OCR"
    echo
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
    
    # Check system requirements
    check_system_requirements
    
    # Create production environment
    create_production_env
    
    # Create configuration directories and files
    create_production_config
    create_security_config
    create_monitoring_config
    
    # Create startup scripts
    create_startup_scripts
    create_backup_script
    
    # Perform security audit
    perform_security_audit
    
    # Validate configuration
    validate_configuration
    
    # Display summary
    display_setup_summary
}

# Run main function
main "$@"

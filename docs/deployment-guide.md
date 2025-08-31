# Vision OCR Deployment Guide

## Overview

This guide covers deploying MarkItDown with Vision OCR integration in various environments, from development to production. It includes Docker deployment, production setup, monitoring, and scaling considerations.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Production Setup](#production-setup)
4. [Environment Configuration](#environment-configuration)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Scaling Considerations](#scaling-considerations)
7. [Security Considerations](#security-considerations)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores (8+ recommended)
- **RAM**: 8GB (16GB+ recommended)
- **Storage**: 20GB available space
- **OS**: Linux, macOS, or Windows 10/11
- **Network**: Internet access for model downloads

#### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Storage**: 50GB+ SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional)
- **Network**: High-speed internet connection

### Software Requirements

- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-service deployment)
- **Python**: 3.10+ (for direct installation)
- **Ollama**: Latest version
- **Git**: For source code management

## Docker Deployment

### Quick Start with Docker Compose

#### 1. Create Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  markitdown-web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8100:8100"
    environment:
      - HOST=0.0.0.0
      - PORT=8100
      - DEBUG=false
      - LOG_LEVEL=INFO
      - OLLAMA_HOST=http://ollama:11434
      - VISION_OCR_MODEL=llava:7b
      - VISION_OCR_ENABLE_HYBRID=true
      - VISION_OCR_MAX_WORKERS=4
      - VISION_OCR_MEMORY_LIMIT=8192
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./logs:/app/logs
      - markitdown_cache:/app/cache
    depends_on:
      - ollama
    restart: unless-stopped
    networks:
      - markitdown-network

  markitdown-mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - VISION_OCR_MODEL=llava:7b
      - VISION_OCR_ENABLE_HYBRID=true
    depends_on:
      - ollama
    restart: unless-stopped
    networks:
      - markitdown-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
      - ./models:/models
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped
    networks:
      - markitdown-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - markitdown-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - markitdown-web
    restart: unless-stopped
    networks:
      - markitdown-network

volumes:
  ollama_models:
  redis_data:
  markitdown_cache:

networks:
  markitdown-network:
    driver: bridge
```

#### 2. Create Dockerfile

Create `Dockerfile`:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libfontconfig1 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install MarkItDown with Vision OCR
RUN pip install markitdown[vision-ocr-advanced]

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/input /app/output /app/logs /app/cache

# Set permissions
RUN chmod +x /app/scripts/start.sh

# Expose port
EXPOSE 8100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

# Start application
CMD ["/app/scripts/start.sh"]
```

#### 3. Create MCP Dockerfile

Create `Dockerfile.mcp`:

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements-mcp.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-mcp.txt

# Install MarkItDown MCP Server
RUN pip install markitdown-mcp-server[vision-ocr]

# Copy MCP server code
COPY packages/markitdown-mcp-server/ ./packages/markitdown-mcp-server/

# Create start script
RUN echo '#!/bin/bash\npython -m markitdown_mcp_server' > /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]
```

#### 4. Create Requirements Files

Create `requirements.txt`:

```txt
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
aiofiles>=23.2.0

# Vision OCR dependencies
ollama>=0.1.0
PyMuPDF>=1.23.0
opencv-python>=4.5.0
pytesseract>=0.3.10
Pillow>=9.0.0
numpy>=1.21.0

# Advanced features
scikit-learn>=1.0.0
pandas>=1.3.0
joblib>=1.1.0
psutil>=5.8.0

# Monitoring and logging
prometheus-client>=0.19.0
structlog>=23.2.0

# Redis for caching
redis>=5.0.0

# Environment management
python-dotenv>=1.0.0
```

Create `requirements-mcp.txt`:

```txt
# MCP dependencies
mcp>=1.13.0

# Vision OCR dependencies
ollama>=0.1.0
PyMuPDF>=1.23.0
opencv-python>=4.5.0
pytesseract>=0.3.10
Pillow>=9.0.0
numpy>=1.21.0

# Advanced features
scikit-learn>=1.0.0
pandas>=1.3.0
joblib>=1.1.0
psutil>=5.8.0
```

#### 5. Create Start Script

Create `scripts/start.sh`:

```bash
#!/bin/bash

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -s http://ollama:11434/api/tags > /dev/null; do
    echo "Ollama not ready, waiting..."
    sleep 5
done

# Pull required models
echo "Pulling required models..."
ollama pull llava:7b
ollama pull llava:13b

# Start the application
echo "Starting MarkItDown Web UI..."
exec uvicorn markitdown_web_ui.app:create_app --host 0.0.0.0 --port 8100 --workers 4
```

#### 6. Create Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream markitdown {
        server markitdown-web:8100;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;

    server {
        listen 80;
        server_name localhost;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name localhost;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # File upload size
        client_max_body_size 100M;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://markitdown;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # File upload endpoint
        location /api/vision-ocr/convert {
            limit_req zone=upload burst=5 nodelay;
            
            proxy_pass http://markitdown;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Longer timeouts for file processing
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }

        # Static files
        location / {
            proxy_pass http://markitdown;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 7. Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f markitdown-web

# Scale services
docker-compose up -d --scale markitdown-web=3
```

### Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  markitdown-web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8100:8100"
    environment:
      - HOST=0.0.0.0
      - PORT=8100
      - DEBUG=false
      - LOG_LEVEL=INFO
      - OLLAMA_HOST=http://ollama:11434
      - VISION_OCR_MODEL=llava:7b
      - VISION_OCR_ENABLE_HYBRID=true
      - VISION_OCR_MAX_WORKERS=8
      - VISION_OCR_MEMORY_LIMIT=16384
      - VISION_OCR_ENABLE_CACHING=true
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./logs:/app/logs
      - markitdown_cache:/app/cache
    depends_on:
      - ollama
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 16G
          cpus: '8.0'
        reservations:
          memory: 8G
          cpus: '4.0'
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    networks:
      - markitdown-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
      - ./models:/models
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 32G
          cpus: '16.0'
        reservations:
          memory: 16G
          cpus: '8.0'
        reservations:
          devices:
            - driver: nvidia
              count: 2
              capabilities: [gpu]
    networks:
      - markitdown-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    networks:
      - markitdown-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - markitdown-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped
    networks:
      - markitdown-network

volumes:
  ollama_models:
  redis_data:
  markitdown_cache:
  prometheus_data:
  grafana_data:

networks:
  markitdown-network:
    driver: bridge
```

## Production Setup

### Environment Configuration

Create `.env.production`:

```bash
# Application Settings
HOST=0.0.0.0
PORT=8100
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (if using)
DATABASE_URL=postgresql://user:password@localhost/markitdown

# Redis
REDIS_URL=redis://redis:6379

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_TIMEOUT=300
OLLAMA_RETRY_ATTEMPTS=3

# Vision OCR Model Settings
VISION_OCR_MODEL=llava:7b
VISION_OCR_STRATEGY=balanced
VISION_OCR_ENABLE_HYBRID=true
VISION_OCR_MAX_WORKERS=8
VISION_OCR_TIMEOUT=300
VISION_OCR_MEMORY_LIMIT=16384
VISION_OCR_ENABLE_CACHING=true
VISION_OCR_QUALITY_THRESHOLD=0.7

# Performance Tuning
VISION_OCR_MAX_CONCURRENT_TASKS=8
VISION_OCR_MAX_RETRIES=3
VISION_OCR_TIMEOUT_MULTIPLIER=1.0
VISION_OCR_CPU_LIMIT_PERCENT=80
VISION_OCR_CACHE_TTL_HOURS=24
VISION_OCR_ENABLE_COMPRESSION=true
VISION_OCR_COMPRESSION_QUALITY=85

# Quality Control
VISION_OCR_ENABLE_QUALITY_PREDICTION=true
VISION_OCR_ENABLE_AUTO_RETRY=true
VISION_OCR_MAX_RETRY_ATTEMPTS=2
VISION_OCR_QUALITY_IMPROVEMENT_THRESHOLD=0.1
VISION_OCR_ENABLE_FALLBACK_STRATEGIES=true

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_MULTIPROC_DIR=/tmp
```

### Systemd Service Configuration

Create `/etc/systemd/system/markitdown.service`:

```ini
[Unit]
Description=MarkItDown Vision OCR Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/markitdown
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### SSL Certificate Setup

#### Using Let's Encrypt

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Using Self-Signed Certificate (Development)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### Firewall Configuration

```bash
# Allow necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8100/tcp
sudo ufw allow 11434/tcp

# Enable firewall
sudo ufw enable
```

## Monitoring and Logging

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
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
  - job_name: 'markitdown-web'
    static_configs:
      - targets: ['markitdown-web:8100']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
    metrics_path: '/api/metrics'
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Grafana Dashboards

Create `grafana/dashboards/markitdown-dashboard.json`:

```json
{
  "dashboard": {
    "id": null,
    "title": "MarkItDown Vision OCR Dashboard",
    "tags": ["markitdown", "vision-ocr"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Processing Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(markitdown_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Processing Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(markitdown_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "id": 3,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "markitdown_memory_usage_bytes",
            "legendFormat": "Memory Usage"
          }
        ]
      },
      {
        "id": 4,
        "title": "Quality Scores",
        "type": "graph",
        "targets": [
          {
            "expr": "markitdown_quality_score",
            "legendFormat": "Quality Score"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

Create `logging.conf`:

```ini
[loggers]
keys=root,markitdown,vision_ocr

[handlers]
keys=consoleHandler,fileHandler,jsonHandler

[formatters]
keys=simpleFormatter,jsonFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_markitdown]
level=INFO
handlers=fileHandler,jsonHandler
qualname=markitdown
propagate=0

[logger_vision_ocr]
level=DEBUG
handlers=fileHandler,jsonHandler
qualname=markitdown.converter_utils.vision_ocr
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=simpleFormatter
args=('logs/markitdown.log', 'a', 10485760, 5)

[handler_jsonHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=jsonFormatter
args=('logs/markitdown.json', 'a', 10485760, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S

[formatter_jsonFormatter]
format={"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}
datefmt=%Y-%m-%d %H:%M:%S
```

## Scaling Considerations

### Horizontal Scaling

#### Load Balancer Configuration

Create `nginx-load-balancer.conf`:

```nginx
upstream markitdown_backend {
    least_conn;
    server markitdown-web-1:8100 max_fails=3 fail_timeout=30s;
    server markitdown-web-2:8100 max_fails=3 fail_timeout=30s;
    server markitdown-web-3:8100 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://markitdown_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    }
}
```

#### Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: markitdown-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: markitdown-web
  template:
    metadata:
      labels:
        app: markitdown-web
    spec:
      containers:
      - name: markitdown-web
        image: markitdown:latest
        ports:
        - containerPort: 8100
        env:
        - name: OLLAMA_HOST
          value: "http://ollama-service:11434"
        - name: VISION_OCR_MODEL
          value: "llava:7b"
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        livenessProbe:
          httpGet:
            path: /health
            port: 8100
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8100
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: markitdown-service
spec:
  selector:
    app: markitdown-web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8100
  type: LoadBalancer
```

### Vertical Scaling

#### Resource Optimization

```python
# Optimize for high-performance systems
settings = {
    "max_workers": 16,
    "max_concurrent_tasks": 16,
    "memory_limit_mb": 32768,
    "cpu_limit_percent": 90,
    "enable_caching": True,
    "cache_ttl_hours": 48,
    "enable_compression": True,
    "compression_quality": 90
}
```

#### GPU Optimization

```bash
# Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## Security Considerations

### Network Security

```bash
# Configure firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 10.0.0.0/8 to any port 8100
sudo ufw enable
```

### Application Security

```python
# Security headers
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60

# File upload restrictions
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_FILE_TYPES = ["pdf", "jpg", "jpeg", "png", "tiff"]
```

### Data Protection

```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

def encrypt_config(config_data):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(config_data).encode())
    return encrypted_data, key

def decrypt_config(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())
```

## Backup and Recovery

### Configuration Backup

```bash
#!/bin/bash
# backup-config.sh

BACKUP_DIR="/backup/config"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration files
tar -czf $BACKUP_DIR/markitdown_config_$DATE.tar.gz \
    ~/.markitdown/config/ \
    .env.production \
    docker-compose.prod.yml

# Backup models (if needed)
tar -czf $BACKUP_DIR/ollama_models_$DATE.tar.gz \
    /var/lib/docker/volumes/markitdown_ollama_models/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Data Recovery

```bash
#!/bin/bash
# restore-config.sh

BACKUP_FILE=$1
RESTORE_DIR="/tmp/restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Create restore directory
mkdir -p $RESTORE_DIR

# Extract backup
tar -xzf $BACKUP_FILE -C $RESTORE_DIR

# Restore configuration
cp -r $RESTORE_DIR/.markitdown/config/ ~/.markitdown/
cp $RESTORE_DIR/.env.production ./
cp $RESTORE_DIR/docker-compose.prod.yml ./

# Restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

echo "Configuration restored successfully"
```

## Troubleshooting

### Common Deployment Issues

#### 1. Container Startup Issues

```bash
# Check container logs
docker-compose logs markitdown-web

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart markitdown-web

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 2. Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limits
docker-compose down
docker-compose -f docker-compose.prod.yml up -d

# Monitor memory usage
watch -n 1 'docker stats --no-stream'
```

#### 3. Network Issues

```bash
# Check network connectivity
docker exec markitdown-web ping ollama

# Check port availability
netstat -tulpn | grep :8100

# Restart network
docker network prune
docker-compose down
docker-compose up -d
```

#### 4. Model Loading Issues

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull models manually
docker exec ollama ollama pull llava:7b

# Check model availability
docker exec ollama ollama list
```

### Performance Monitoring

```bash
# Monitor system resources
htop
iotop
nvidia-smi  # If using GPU

# Monitor application metrics
curl http://localhost:8100/metrics

# Check logs for errors
tail -f logs/markitdown.log | grep ERROR

# Monitor disk usage
df -h
du -sh /var/lib/docker/volumes/
```

### Health Checks

```bash
# Application health
curl http://localhost:8100/health

# Ollama health
curl http://localhost:11434/api/tags

# Redis health
redis-cli ping

# Database health (if using)
psql $DATABASE_URL -c "SELECT 1;"
```

This comprehensive deployment guide provides everything needed to deploy MarkItDown with Vision OCR integration in production environments, including Docker deployment, monitoring, scaling, security, and troubleshooting.

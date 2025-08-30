# MarkItDown Web UI Deployment Guide

This guide covers deploying the MarkItDown Web UI with configurable input/output directories for different use cases.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration Options](#configuration-options)
4. [Deployment Methods](#deployment-methods)
5. [Use Case Examples](#use-case-examples)
6. [Production Deployment](#production-deployment)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB of available RAM
- 10GB of available disk space
- Port 8100 available (configurable)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd markitdown
```

### 2. Deploy with Default Settings

```bash
# Using the deployment script
./scripts/deploy.sh

# Or manually with Docker Compose
docker-compose up -d
```

### 3. Access the Application

- **Web UI**: http://localhost:8100
- **API Documentation**: http://localhost:8100/docs
- **Health Check**: http://localhost:8100/health

## Configuration Options

### Environment Variables

The application can be configured using environment variables or the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_DIR` | `./input` | Input directory for files to process |
| `OUTPUT_DIR` | `./output` | Output directory for converted files |
| `PORT` | `8100` | Port to expose the web UI |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE` | `100MB` | Maximum file size for uploads |
| `ALLOWED_FILE_TYPES` | `pdf,docx,txt,jpg,png,html` | Allowed file extensions |

### Directory Configuration

The application supports configurable input and output directories for different workflows:

```bash
# Document processing workflow
INPUT_DIR=/path/to/documents
OUTPUT_DIR=/path/to/processed

# Image processing workflow  
INPUT_DIR=/path/to/images
OUTPUT_DIR=/path/to/converted

# Batch processing workflow
INPUT_DIR=/path/to/batch/input
OUTPUT_DIR=/path/to/batch/output
```

## Deployment Methods

### 1. Using Deployment Scripts

#### Linux/macOS
```bash
# Default deployment
./scripts/deploy.sh

# Custom directories
./scripts/deploy.sh -i /path/to/input -o /path/to/output

# Custom port
./scripts/deploy.sh -p 8200

# Development mode
./scripts/deploy.sh -d
```

#### Windows
```cmd
# Default deployment
scripts\deploy.bat

# Custom directories
scripts\deploy.bat -i C:\path\to\input -o C:\path\to\output

# Custom port
scripts\deploy.bat -p 8200

# Development mode
scripts\deploy.bat -d
```

### 2. Manual Docker Compose

```bash
# Set environment variables
export INPUT_DIR=/path/to/input
export OUTPUT_DIR=/path/to/output
export PORT=8100

# Start the application
docker-compose up -d

# With production profile (includes nginx)
docker-compose --profile production up -d
```

### 3. Docker Run

```bash
docker run -d \
  --name markitdown-web-ui \
  -p 8100:8100 \
  -v /path/to/input:/app/input:rw \
  -v /path/to/output:/app/output:rw \
  -e INPUT_DIR=/app/input \
  -e OUTPUT_DIR=/app/output \
  markitdown-web-ui:latest
```

## Use Case Examples

### 1. Document Processing Workflow

For processing documents in a shared folder:

```bash
# Deploy with document directories
./scripts/deploy.sh \
  -i /shared/documents \
  -o /shared/processed \
  -p 8100

# Access via web UI to upload and convert documents
# Converted files will be saved to /shared/processed
```

### 2. Image Processing Workflow

For converting images to markdown descriptions:

```bash
# Deploy with image directories
./scripts/deploy.sh \
  -i /photos/raw \
  -o /photos/converted \
  -p 8200

# Upload images via web UI
# Get markdown descriptions in /photos/converted
```

### 3. Batch Processing Workflow

For automated batch processing:

```bash
# Deploy with batch directories
./scripts/deploy.sh \
  -i /batch/input \
  -o /batch/output \
  -p 8300

# Place files in /batch/input
# Process via API or web UI
# Results in /batch/output
```

### 4. Development Environment

For development with live code reloading:

```bash
# Deploy in development mode
./scripts/deploy.sh -d

# Source code changes will be reflected immediately
# Logs are more verbose
```

## Production Deployment

### 1. Production Configuration

Create a production `.env` file:

```bash
# Production environment variables
HOST=0.0.0.0
PORT=8100
DEBUG=false
LOG_LEVEL=WARNING

# Production directories
INPUT_DIR=/data/input
OUTPUT_DIR=/data/output

# Security settings
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,localhost

# Performance settings
MAX_FILE_SIZE=500MB
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60
```

### 2. Production Deployment with Nginx

```bash
# Deploy with production profile
docker-compose --profile production up -d

# This includes:
# - MarkItDown Web UI on port 8100
# - Nginx reverse proxy on ports 80/443
# - Rate limiting and security headers
# - SSL termination (configure certificates)
```

### 3. Kubernetes Deployment

Create a Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: markitdown-web-ui
spec:
  replicas: 3
  selector:
    matchLabels:
      app: markitdown-web-ui
  template:
    metadata:
      labels:
        app: markitdown-web-ui
    spec:
      containers:
      - name: markitdown-web-ui
        image: markitdown-web-ui:latest
        ports:
        - containerPort: 8100
        env:
        - name: INPUT_DIR
          value: "/app/input"
        - name: OUTPUT_DIR
          value: "/app/output"
        volumeMounts:
        - name: input-volume
          mountPath: /app/input
        - name: output-volume
          mountPath: /app/output
      volumes:
      - name: input-volume
        persistentVolumeClaim:
          claimName: input-pvc
      - name: output-volume
        persistentVolumeClaim:
          claimName: output-pvc
```

## Monitoring and Maintenance

### 1. Health Checks

```bash
# Check application health
curl http://localhost:8100/health

# Check directory status
curl http://localhost:8100/api/directories/config
```

### 2. Logs

```bash
# View application logs
docker-compose logs -f markitdown-web-ui

# View nginx logs (production)
docker-compose logs -f nginx
```

### 3. Backup and Recovery

```bash
# Backup input/output directories
tar -czf backup-$(date +%Y%m%d).tar.gz /path/to/input /path/to/output

# Restore from backup
tar -xzf backup-20240115.tar.gz -C /
```

### 4. Updates

```bash
# Update the application
git pull
docker-compose down
docker-compose up -d --build
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using the port
lsof -i :8100

# Use a different port
./scripts/deploy.sh -p 8200
```

#### 2. Permission Denied

```bash
# Fix directory permissions
sudo chown -R $USER:$USER /path/to/input /path/to/output
chmod 755 /path/to/input /path/to/output
```

#### 3. Docker Not Running

```bash
# Start Docker service
sudo systemctl start docker

# Check Docker status
docker info
```

#### 4. Insufficient Disk Space

```bash
# Check disk usage
df -h

# Clean up Docker images
docker system prune -a
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set debug environment variable
export DEBUG=true

# Restart the application
docker-compose restart markitdown-web-ui

# Check detailed logs
docker-compose logs -f markitdown-web-ui
```

### API Testing

Test the API endpoints:

```bash
# Test health endpoint
curl http://localhost:8100/health

# Test directory listing
curl http://localhost:8100/api/directories/input

# Test file upload
curl -X POST -F "file=@test.pdf" http://localhost:8100/api/directories/input/upload
```

## Support

For additional support:

1. Check the [API Documentation](http://localhost:8100/docs)
2. Review the [Integration Guide](docs/integration-guide.md)
3. Check the [Troubleshooting Guide](docs/troubleshooting.md)
4. Open an issue on GitHub

## Security Considerations

1. **Change default secret key** in production
2. **Configure proper firewall rules**
3. **Use HTTPS in production**
4. **Regular security updates**
5. **Monitor access logs**
6. **Backup important data regularly**

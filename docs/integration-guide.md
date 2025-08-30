# MarkItDown Integration Guide

## Overview

This guide provides comprehensive instructions for integrating MarkItDown MCP tools and FastAPI web UI into your applications. It covers setup, configuration, deployment, and troubleshooting.

## Table of Contents

1. [MCP Server Setup](#mcp-server-setup)
2. [FastAPI-MCP Integration](#fastapi-mcp-integration)
3. [Deployment Procedures](#deployment-procedures)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Advanced Configuration](#advanced-configuration)

## MCP Server Setup

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/microsoft/markitdown.git
   cd markitdown
   ```

2. **Set up development environment:**
   ```bash
   # Using the setup script (recommended)
   ./scripts/setup-dev.sh
   
   # Or using make
   make setup-dev
   ```

3. **Install MCP server package:**
   ```bash
   cd packages/markitdown-mcp-server
   uv pip install -e ".[dev]"
   ```

### Configuration

Create a configuration file `config.yaml`:

```yaml
# MCP Server Configuration
server:
  host: "0.0.0.0"
  port: 8001
  debug: false

# MarkItDown Configuration
markitdown:
  plugins_directory: "./plugins"
  temp_directory: "./temp"
  max_file_size: 104857600  # 100MB
  supported_formats:
    - pdf
    - docx
    - html
    - txt
    - md

# Logging Configuration
logging:
  level: "INFO"
  file: "./logs/mcp_server.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Security Configuration
security:
  allowed_origins: ["*"]
  api_key_required: false
  rate_limit_enabled: true
  rate_limit_requests: 100
  rate_limit_window: 60
```

### Running the MCP Server

1. **Start the MCP server:**
   ```bash
   cd packages/markitdown-mcp-server
   python -m markitdown_mcp_server
   ```

2. **Verify the server is running:**
   ```bash
   curl http://localhost:8001/health
   ```

3. **Test MCP tools:**
   ```bash
   # List available tools
   curl http://localhost:8001/mcp/tools
   
   # Test format detection
   curl -X POST http://localhost:8001/mcp/detect \
     -F "file=@test.pdf"
   ```

### MCP Server API

The MCP server exposes the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/mcp/tools` | GET | List available tools |
| `/mcp/call` | POST | Call MCP tool |
| `/mcp/convert` | POST | Convert single file |
| `/mcp/batch` | POST | Convert multiple files |
| `/mcp/detect` | POST | Detect file format |
| `/mcp/formats` | GET | List supported formats |
| `/mcp/plugins` | GET | List available plugins |

## FastAPI-MCP Integration

### Overview

The FastAPI-MCP integration allows you to expose MCP tools as REST API endpoints, making them accessible to web applications and other services.

### Integration Methods

#### Method 1: Direct Integration (Recommended)

```python
from fastapi import FastAPI
from fastapi_mcp import FastAPIMCP
from markitdown_mcp_server.server import MarkItDownMCPServer

app = FastAPI(title="MarkItDown API")

# Create MCP server instance
mcp_server = MarkItDownMCPServer()

# Mount MCP tools to FastAPI
mcp_integration = FastAPIMCP(mcp_server)
app.include_router(mcp_integration.router, prefix="/mcp", tags=["MCP Tools"])
```

#### Method 2: Simulated Integration (Development)

For development without a running MCP server:

```python
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI(title="MarkItDown API")

# Create simulated MCP router
mcp_router = APIRouter(prefix="/mcp", tags=["MCP Tools"])

class MCPRequest(BaseModel):
    tool_name: str
    arguments: dict

@mcp_router.post("/call")
async def call_mcp_tool(request: MCPRequest):
    # Simulate MCP tool call
    return {"success": True, "data": {"result": "simulated"}}

app.include_router(mcp_router)
```

### Configuration

Create a FastAPI configuration file:

```python
# config/fastapi_config.py
from pydantic_settings import BaseSettings

class FastAPISettings(BaseSettings):
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8100
    debug: bool = False
    
    # MCP integration settings
    mcp_server_url: str = "http://localhost:8001"
    mcp_timeout: int = 30
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_methods: list = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: list = ["*"]
    
    # File upload settings
    max_file_size: int = 104857600  # 100MB
    upload_directory: str = "./uploads"
    
    class Config:
        env_file = ".env"
```

### Environment Variables

Create a `.env` file:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8100
DEBUG=false

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001
MCP_TIMEOUT=30

# File Upload Configuration
MAX_FILE_SIZE=104857600
UPLOAD_DIRECTORY=./uploads

# Security Configuration
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=*

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/fastapi.log
```

### Running the FastAPI Application

1. **Start the FastAPI application:**
   ```bash
   cd packages/markitdown-web-ui
   python -m markitdown_web_ui
   ```

2. **Access the API documentation:**
   - Swagger UI: http://localhost:8100/docs
   - ReDoc: http://localhost:8100/redoc

3. **Test the integration:**
   ```bash
   # Health check
   curl http://localhost:8100/health
   
   # List MCP tools
   curl http://localhost:8100/mcp/tools
   
   # Convert a file
   curl -X POST http://localhost:8100/mcp/convert \
     -F "file=@document.pdf" \
     -F "output_format=markdown"
   ```

## Deployment Procedures

### Development Deployment

#### Using Docker Compose

1. **Create docker-compose.yml:**

```yaml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: packages/markitdown-mcp-server/Dockerfile
    ports:
      - "8001:8001"
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    environment:
      - MCP_SERVER_HOST=0.0.0.0
      - MCP_SERVER_PORT=8001
      - LOG_LEVEL=INFO
    networks:
      - markitdown-network

  web-ui:
    build:
      context: .
      dockerfile: packages/markitdown-web-ui/Dockerfile
    ports:
      - "8100:8100"
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    environment:
      - WEB_UI_HOST=0.0.0.0
      - WEB_UI_PORT=8100
      - MCP_SERVER_URL=http://mcp-server:8001
      - LOG_LEVEL=INFO
    depends_on:
      - mcp-server
    networks:
      - markitdown-network

networks:
  markitdown-network:
    driver: bridge

volumes:
  uploads:
  logs:
```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

#### Using Systemd (Linux)

1. **Create systemd service files:**

```ini
# /etc/systemd/system/markitdown-mcp.service
[Unit]
Description=MarkItDown MCP Server
After=network.target

[Service]
Type=simple
User=markitdown
WorkingDirectory=/opt/markitdown/packages/markitdown-mcp-server
Environment=PATH=/opt/markitdown/.venv/bin
ExecStart=/opt/markitdown/.venv/bin/python -m markitdown_mcp_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/markitdown-web.service
[Unit]
Description=MarkItDown Web UI
After=network.target markitdown-mcp.service

[Service]
Type=simple
User=markitdown
WorkingDirectory=/opt/markitdown/packages/markitdown-web-ui
Environment=PATH=/opt/markitdown/.venv/bin
ExecStart=/opt/markitdown/.venv/bin/python -m markitdown_web_ui
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start services:**
   ```bash
   sudo systemctl enable markitdown-mcp
   sudo systemctl enable markitdown-web
   sudo systemctl start markitdown-mcp
   sudo systemctl start markitdown-web
   ```

### Production Deployment

#### Using Nginx as Reverse Proxy

1. **Install Nginx:**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Create Nginx configuration:**

```nginx
# /etc/nginx/sites-available/markitdown
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Client max body size
    client_max_body_size 100M;

    # Web UI
    location / {
        proxy_pass http://localhost:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MCP endpoints
    location /mcp/ {
        proxy_pass http://localhost:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable the site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/markitdown /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

#### Using Docker in Production

1. **Create production Dockerfile:**

```dockerfile
# packages/markitdown-web-ui/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 markitdown && \
    chown -R markitdown:markitdown /app
USER markitdown

# Expose port
EXPOSE 8100

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

# Start application
CMD ["uvicorn", "markitdown_web_ui.app:create_app", "--host", "0.0.0.0", "--port", "8100"]
```

2. **Build and deploy:**
   ```bash
   docker build -f packages/markitdown-web-ui/Dockerfile.prod -t markitdown-web:latest .
   docker run -d -p 8100:8100 --name markitdown-web markitdown-web:latest
   ```

## Troubleshooting Guide

### Common Issues

#### 1. MCP Server Not Starting

**Symptoms:**
- MCP server fails to start
- Connection refused errors

**Solutions:**
```bash
# Check if port is already in use
sudo netstat -tulpn | grep :8001

# Check logs
tail -f packages/markitdown-mcp-server/logs/mcp_server.log

# Restart the service
sudo systemctl restart markitdown-mcp
```

#### 2. FastAPI Application Not Starting

**Symptoms:**
- FastAPI application fails to start
- Import errors

**Solutions:**
```bash
# Check Python environment
python --version
pip list | grep markitdown

# Reinstall packages
cd packages/markitdown-web-ui
uv pip install -e ".[dev]"

# Check logs
tail -f packages/markitdown-web-ui/logs/fastapi.log
```

#### 3. File Conversion Failures

**Symptoms:**
- File conversion returns errors
- Unsupported format errors

**Solutions:**
```bash
# Check supported formats
curl http://localhost:8100/mcp/formats

# Check plugin status
curl http://localhost:8100/mcp/plugins

# Verify file format
file your-document.pdf
```

#### 4. Performance Issues

**Symptoms:**
- Slow conversion times
- High memory usage

**Solutions:**
```bash
# Monitor system resources
htop
df -h

# Check application logs for errors
tail -f packages/markitdown-web-ui/logs/fastapi.log

# Optimize configuration
# Increase max_file_size in config
# Enable parallel processing
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set environment variables
export WEB_UI_DEBUG=true
export MCP_SERVER_DEBUG=true
export LOG_LEVEL=DEBUG

# Restart services
sudo systemctl restart markitdown-mcp
sudo systemctl restart markitdown-web
```

### Log Analysis

#### MCP Server Logs

```bash
# View real-time logs
tail -f packages/markitdown-mcp-server/logs/mcp_server.log

# Search for errors
grep -i error packages/markitdown-mcp-server/logs/mcp_server.log

# Search for specific tool calls
grep "convert_file" packages/markitdown-mcp-server/logs/mcp_server.log
```

#### FastAPI Logs

```bash
# View real-time logs
tail -f packages/markitdown-web-ui/logs/fastapi.log

# Search for errors
grep -i error packages/markitdown-web-ui/logs/fastapi.log

# Search for specific endpoints
grep "POST /mcp/convert" packages/markitdown-web-ui/logs/fastapi.log
```

### Health Checks

Create a health check script:

```bash
#!/bin/bash
# health_check.sh

# Check MCP server
echo "Checking MCP server..."
curl -f http://localhost:8001/health || echo "MCP server is down"

# Check FastAPI application
echo "Checking FastAPI application..."
curl -f http://localhost:8100/health || echo "FastAPI application is down"

# Check disk space
echo "Checking disk space..."
df -h | grep -E "(Filesystem|/dev/)"

# Check memory usage
echo "Checking memory usage..."
free -h

# Check running processes
echo "Checking running processes..."
ps aux | grep -E "(markitdown|python)" | grep -v grep
```

## Advanced Configuration

### Custom Plugins

1. **Create a custom plugin:**

```python
# plugins/custom_converter.py
from markitdown.plugins.base import BaseConverter

class CustomConverter(BaseConverter):
    name = "custom_converter"
    supported_formats = [".custom"]
    
    def convert(self, input_path: str, output_path: str, options: dict = None):
        # Custom conversion logic
        pass
```

2. **Register the plugin:**

```python
# In your MCP server configuration
from plugins.custom_converter import CustomConverter

# Register the plugin
mcp_server.register_plugin(CustomConverter())
```

### Custom MCP Tools

1. **Create a custom MCP tool:**

```python
# tools/custom_tool.py
from markitdown_mcp_server.tools.base import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Custom tool for specific operations"
    
    def execute(self, arguments: dict) -> dict:
        # Custom tool logic
        return {"result": "custom operation completed"}
```

2. **Register the tool:**

```python
# In your MCP server
from tools.custom_tool import CustomTool

# Register the tool
mcp_server.register_tool(CustomTool())
```

### Monitoring and Metrics

1. **Enable Prometheus metrics:**

```python
# Add to FastAPI application
from prometheus_fastapi_instrumentator import Instrumentator

# Instrument the app
Instrumentator().instrument(app).expose(app)
```

2. **Create monitoring dashboard:**

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Security Hardening

1. **Enable authentication:**

```python
# Add to FastAPI application
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-api-key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

# Apply to endpoints
@app.post("/mcp/convert")
async def convert_file(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    # Conversion logic
    pass
```

2. **Rate limiting:**

```python
# Add to FastAPI application
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/mcp/convert")
@limiter.limit("10/minute")
async def convert_file(request: Request, file: UploadFile = File(...)):
    # Conversion logic
    pass
```

This comprehensive integration guide provides everything needed to set up, configure, deploy, and troubleshoot the MarkItDown MCP tools and FastAPI web UI integration.

# MarkItDown

[![PyPI](https://img.shields.io/pypi/v/markitdown.svg)](https://pypi.org/project/markitdown/)
![PyPI - Downloads](https://img.shields.io/pypi/dd/markitdown)
[![Built by AutoGen Team](https://img.shields.io/badge/Built%20by-AutoGen%20Team-blue)](https://github.com/microsoft/autogen)

> [!TIP]
> MarkItDown now offers an MCP (Model Context Protocol) server and FastAPI web UI for enhanced integration and user experience. See [MCP Tools](#mcp-tools) and [Web UI](#web-ui) sections for more information.

> [!IMPORTANT]
> Breaking changes between 0.0.1 to 0.1.0:
> * Dependencies are now organized into optional feature-groups (further details below). Use `pip install 'markitdown[all]'` to have backward-compatible behavior. 
> * convert\_stream() now requires a binary file-like object (e.g., a file opened in binary mode, or an io.BytesIO object). This is a breaking change from the previous version, where it previously also accepted text file-like objects, like io.StringIO.
> * The DocumentConverter class interface has changed to read from file-like streams rather than file paths. *No temporary files are created anymore*. If you are the maintainer of a plugin, or custom DocumentConverter, you likely need to update your code. Otherwise, if only using the MarkItDown class or CLI (as in these examples), you should not need to change anything.

MarkItDown is a lightweight Python utility for converting various files to Markdown for use with LLMs and related text analysis pipelines. To this end, it is most comparable to [textract](https://github.com/deanmalmgren/textract), but with a focus on preserving important document structure and content as Markdown (including: headings, lists, tables, links, etc.) While the output is often reasonably presentable and human-friendly, it is meant to be consumed by text analysis tools -- and may not be the best option for high-fidelity document conversions for human consumption.

## 🚀 New Features

### MCP (Model Context Protocol) Tools
MarkItDown now provides MCP tools for seamless integration with LLM applications like Claude Desktop:

- **File Conversion**: Convert individual files to Markdown
- **Batch Processing**: Convert multiple files simultaneously
- **Format Detection**: Automatically detect file formats
- **Plugin Management**: List and manage available plugins
- **Supported Formats**: Get comprehensive format support information

### FastAPI Web UI
A modern web interface for easy file conversion:

- **Drag & Drop**: Simple file upload interface
- **Batch Processing**: Convert multiple files at once
- **Real-time Updates**: Monitor conversion progress
- **RESTful API**: Programmatic access to all features
- **Auto-detection**: Automatic format detection and conversion
- **Configurable Directories**: Map local folders for input/output
- **Port 8200**: Exposed to local PC for easy access

### Production-Ready Deployment
Complete deployment solution with:

- **Docker Containerization**: Easy deployment and scaling
- **Configurable Volumes**: Map local directories for different workflows
- **Nginx Reverse Proxy**: Production-ready with rate limiting and security
- **CI/CD Pipeline**: Automated testing and deployment
- **Health Monitoring**: Built-in health checks and logging
- **Cross-Platform Scripts**: Deployment scripts for Linux/macOS and Windows

### Phase 6: Enterprise Production Preparation
**Status**: ✅ Completed | **Progress**: 100%

Phase 6 transformed MarkItDown into an enterprise-grade production solution with comprehensive security, monitoring, scalability, and deployment automation:

#### 🏭 Production Environment
- **Multi-Service Docker Architecture**: Complete service stack with MarkItDown Web UI, MCP Server, Ollama, PostgreSQL, Redis, Nginx, and monitoring services
- **Multi-Stage Production Dockerfile**: Security-hardened containers with GPU support and vulnerability scanning
- **Automated Production Setup**: System validation, environment configuration, and security hardening
- **Resource Management**: CPU and memory limits with proper resource allocation and health checks

#### ⚡ Performance Optimization
- **System Performance Tuning**: CPU optimization, memory management, network tuning, and Docker optimization
- **Vision OCR Optimization**: Model caching, batch processing, and GPU acceleration
- **Performance Monitoring**: Real-time resource monitoring, load testing, and benchmark automation
- **Advanced Performance Configuration**: Database optimization, cache management, and concurrent processing

#### 🔒 Security Hardening
- **Comprehensive Security Audit**: Container security, code security, dependency security, and system security
- **Security Configurations**: AppArmor profiles, firewall rules, SSL/TLS configuration, and authentication
- **Security Monitoring**: Real-time security monitoring, compliance reporting, and vulnerability management
- **Compliance Frameworks**: SOC 2, GDPR, HIPAA, and PCI DSS compliance support

#### 🔄 CI/CD Pipeline Enhancement
- **GitHub Actions Workflow**: Multi-stage pipeline with security scanning, testing, building, and deployment
- **Deployment Automation**: Infrastructure as code, environment management, and service discovery
- **Quality Assurance**: Code quality, test coverage, performance regression, and documentation automation
- **Blue-Green Deployment**: Zero-downtime deployment strategy with automated rollback

#### 📊 Monitoring and Observability
- **Comprehensive Monitoring Stack**: Prometheus, Grafana, AlertManager, and ELK stack
- **Custom Vision OCR Monitoring**: Processing metrics, model performance, and quality metrics
- **Health Monitoring**: Service health, resource monitoring, and business metrics
- **Automated Remediation**: Self-healing capabilities for common issues

#### 🚀 Scalability and High Availability
- **Horizontal Scaling**: Kubernetes support, auto-scaling, and load distribution
- **High Availability Features**: Service redundancy, failover procedures, and data replication
- **Disaster Recovery**: Automated backups, recovery procedures, and business continuity
- **Geographic Distribution**: Multi-region deployment support

## 📊 Project Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI[Command Line Interface]
        WebUI[FastAPI Web UI<br/>Port 8200]
        MCP[MCP Tools]
        API[RESTful API]
    end
    
    subgraph "Core Services"
        MarkItDown[MarkItDown Core]
        MCP_Server[MCP Server]
        Web_Server[FastAPI Server]
        Nginx[Nginx Reverse Proxy<br/>Port 80/443]
    end
    
    subgraph "File Processing"
        Converters[File Converters]
        Plugins[Plugin System]
        Formats[Format Detection]
        Batch[Batch Processing]
    end
    
    subgraph "Deployment"
        Docker[Docker Container]
        Volumes[Configurable Volumes<br/>Input/Output]
        CI_CD[CI/CD Pipeline]
        Monitoring[Health Checks]
    end
    
    subgraph "Output"
        Markdown[Markdown Output]
        Metadata[File Metadata]
        Errors[Error Handling]
        Logs[Structured Logging]
    end
    
    CLI --> MarkItDown
    WebUI --> Web_Server
    MCP --> MCP_Server
    API --> Web_Server
    
    Web_Server --> MarkItDown
    MCP_Server --> MarkItDown
    Nginx --> Web_Server
    
    MarkItDown --> Converters
    MarkItDown --> Plugins
    MarkItDown --> Formats
    MarkItDown --> Batch
    
    Converters --> Markdown
    Plugins --> Markdown
    Formats --> Metadata
    Batch --> Markdown
    
    Docker --> Volumes
    Docker --> Monitoring
    CI_CD --> Docker
    
    MarkItDown --> Errors
    MarkItDown --> Logs
```

## 🔧 Package Structure

```mermaid
graph LR
    subgraph "MarkItDown Workspace"
        Core[markitdown<br/>Core Library]
        MCP_Server[markitdown-mcp-server<br/>MCP Tools]
        Web_UI[markitdown-web-ui<br/>FastAPI UI]
        Sample_Plugin[markitdown-sample-plugin<br/>Example Plugin]
        MCP_Client[markitdown-mcp<br/>MCP Client]
    end
    
    subgraph "Deployment"
        Docker[Docker Container]
        Scripts[Deployment Scripts]
        Config[Configuration Files]
    end
    
    subgraph "Documentation"
        API_Docs[API Documentation]
        Tool_Cards[Tool Cards]
        Guides[HOW TO Guides]
        Plans[Project Plans]
    end
    
    Core --> MCP_Server
    Core --> Web_UI
    Core --> Sample_Plugin
    MCP_Server --> MCP_Client
    
    Web_UI --> Docker
    Scripts --> Docker
    Config --> Docker
    
    Core --> API_Docs
    MCP_Server --> Tool_Cards
    Web_UI --> Guides
    Docker --> Plans
```

## 🏭 Phase 6: Production Architecture

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Nginx Reverse Proxy<br/>SSL Termination<br/>Rate Limiting<br/>Port 80/443]
    end
    
    subgraph "Application Layer"
        subgraph "Web UI Cluster"
            WebUI1[MarkItDown Web UI<br/>Instance 1]
            WebUI2[MarkItDown Web UI<br/>Instance 2]
            WebUI3[MarkItDown Web UI<br/>Instance N]
        end
        
        subgraph "MCP Server Cluster"
            MCP1[MCP Server<br/>Instance 1]
            MCP2[MCP Server<br/>Instance 2]
            MCP3[MCP Server<br/>Instance N]
        end
        
        subgraph "Vision OCR Processing"
            Vision1[Vision OCR<br/>Worker 1]
            Vision2[Vision OCR<br/>Worker 2]
            VisionN[Vision OCR<br/>Worker N]
        end
    end
    
    subgraph "Data Layer"
        subgraph "Database Cluster"
            PG1[PostgreSQL<br/>Primary]
            PG2[PostgreSQL<br/>Replica 1]
            PG3[PostgreSQL<br/>Replica N]
        end
        
        subgraph "Cache Layer"
            Redis1[Redis<br/>Primary]
            Redis2[Redis<br/>Replica]
        end
        
        subgraph "File Storage"
            Storage[Persistent Storage<br/>Input/Output<br/>Models/Logs]
        end
    end
    
    subgraph "AI/ML Layer"
        subgraph "Ollama Vision Models"
            Ollama1[Ollama<br/>Vision Model 1]
            Ollama2[Ollama<br/>Vision Model 2]
            OllamaN[Ollama<br/>Vision Model N]
        end
        
        subgraph "GPU Acceleration"
            GPU1[GPU Cluster 1<br/>CUDA Enabled]
            GPU2[GPU Cluster 2<br/>CUDA Enabled]
        end
    end
    
    subgraph "Monitoring Stack"
        subgraph "Metrics & Visualization"
            Prometheus[Prometheus<br/>Metrics Collection]
            Grafana[Grafana<br/>Dashboards]
            AlertManager[AlertManager<br/>Notifications]
        end
        
        subgraph "Logging & Analysis"
            Elasticsearch[Elasticsearch<br/>Log Storage]
            Kibana[Kibana<br/>Log Analysis]
            Filebeat[Filebeat<br/>Log Collection]
        end
        
        subgraph "Security Monitoring"
            Trivy[Trivy<br/>Vulnerability Scanner]
            Security[Security<br/>Monitoring]
        end
    end
    
    subgraph "Security Layer"
        subgraph "Network Security"
            Firewall[Firewall<br/>Rules]
            VPN[VPN Access]
        end
        
        subgraph "Container Security"
            AppArmor[AppArmor<br/>Profiles]
            NonRoot[Non-root<br/>Users]
        end
        
        subgraph "Application Security"
            Auth[Authentication<br/>OAuth2/OIDC]
            SSL[SSL/TLS<br/>Certificates]
        end
    end
    
    subgraph "CI/CD Pipeline"
        subgraph "Development"
            GitHub[GitHub<br/>Repository]
            Actions[GitHub Actions<br/>CI/CD]
        end
        
        subgraph "Deployment"
            Staging[Staging<br/>Environment]
            Production[Production<br/>Environment]
            Rollback[Rollback<br/>Procedures]
        end
    end
    
    %% Load Balancer connections
    LB --> WebUI1
    LB --> WebUI2
    LB --> WebUI3
    
    %% Application layer connections
    WebUI1 --> MCP1
    WebUI2 --> MCP2
    WebUI3 --> MCP3
    
    WebUI1 --> Vision1
    WebUI2 --> Vision2
    WebUI3 --> VisionN
    
    %% Data layer connections
    WebUI1 --> PG1
    WebUI2 --> PG1
    WebUI3 --> PG1
    
    WebUI1 --> Redis1
    WebUI2 --> Redis1
    WebUI3 --> Redis1
    
    WebUI1 --> Storage
    WebUI2 --> Storage
    WebUI3 --> Storage
    
    %% Database replication
    PG1 --> PG2
    PG1 --> PG3
    Redis1 --> Redis2
    
    %% AI/ML connections
    Vision1 --> Ollama1
    Vision2 --> Ollama2
    VisionN --> OllamaN
    
    Ollama1 --> GPU1
    Ollama2 --> GPU2
    OllamaN --> GPU1
    
    %% Monitoring connections
    WebUI1 --> Prometheus
    WebUI2 --> Prometheus
    WebUI3 --> Prometheus
    
    Prometheus --> Grafana
    Prometheus --> AlertManager
    
    WebUI1 --> Elasticsearch
    WebUI2 --> Elasticsearch
    WebUI3 --> Elasticsearch
    
    Elasticsearch --> Kibana
    Filebeat --> Elasticsearch
    
    %% Security connections
    Firewall --> LB
    VPN --> Firewall
    
    AppArmor --> WebUI1
    AppArmor --> WebUI2
    AppArmor --> WebUI3
    
    Auth --> WebUI1
    Auth --> WebUI2
    Auth --> WebUI3
    
    SSL --> LB
    
    %% CI/CD connections
    GitHub --> Actions
    Actions --> Staging
    Actions --> Production
    Actions --> Rollback
    
    %% Security scanning
    Trivy --> WebUI1
    Trivy --> WebUI2
    Trivy --> WebUI3
    Security --> AlertManager
```

### Production Deployment Workflow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant CI as CI/CD Pipeline
    participant Sec as Security Scanner
    participant Test as Test Environment
    participant Prod as Production
    participant Monitor as Monitoring Stack
    
    Dev->>GH: Push Code Changes
    GH->>CI: Trigger CI/CD Pipeline
    
    CI->>Sec: Security Scanning
    Sec-->>CI: Security Report
    
    alt Security Issues Found
        CI-->>Dev: Security Alert
    else Security Passed
        CI->>Test: Deploy to Staging
        Test-->>CI: Test Results
        
        alt Tests Failed
            CI-->>Dev: Test Failure Alert
        else Tests Passed
            CI->>Prod: Blue-Green Deployment
            Prod->>Monitor: Health Check
            Monitor-->>Prod: Health Status
            
            alt Health Check Failed
                Prod-->>CI: Rollback to Previous Version
                CI-->>Dev: Deployment Failure
            else Health Check Passed
                Prod-->>CI: Deployment Success
                CI-->>Dev: Deployment Complete
                Monitor->>Monitor: Continuous Monitoring
            end
        end
    end
```

### Performance and Security Metrics

```mermaid
graph LR
    subgraph "Performance Metrics"
        PM1[Response Time<br/>< 2s 95th percentile]
        PM2[Throughput<br/>100+ concurrent users]
        PM3[Resource Usage<br/>< 80% CPU, < 85% memory]
        PM4[Uptime<br/>99.9% availability]
    end
    
    subgraph "Vision OCR Metrics"
        VOM1[Processing Time<br/>5-15 seconds]
        VOM2[Accuracy<br/>> 90% text extraction]
        VOM3[Concurrent Jobs<br/>10+ simultaneous]
        VOM4[Model Loading<br/>< 30 seconds]
    end
    
    subgraph "Security Metrics"
        SM1[Vulnerability Scan<br/>100% pass rate]
        SM2[Compliance<br/>SOC 2, GDPR, HIPAA]
        SM3[Security Monitoring<br/>24/7 real-time]
        SM4[Incident Response<br/>< 10 minutes]
    end
    
    subgraph "Scalability Metrics"
        SC1[Horizontal Scaling<br/>Linear scaling]
        SC2[Auto-scaling<br/>< 5s response time]
        SC3[Load Distribution<br/>Even distribution]
        SC4[Resource Efficiency<br/>Optimal utilization]
    end
```

## 📋 Supported Formats

MarkItDown currently supports the conversion from:

- **Documents**: PDF, PowerPoint, Word, Excel
- **Media**: Images (EXIF metadata and OCR), Audio (transcription)
- **Web**: HTML, YouTube URLs
- **Data**: CSV, JSON, XML
- **Archives**: ZIP files (iterates over contents)
- **E-books**: EPubs
- **Email**: Outlook messages
- **And more!**

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone git@github.com:microsoft/markitdown.git
cd markitdown

# Setup development environment
./scripts/setup-dev.sh  # Linux/Mac
# or
scripts\setup-dev.bat   # Windows

# Or use make
make setup-dev
```

### 2. Start the Web UI

```bash
# Start the FastAPI web UI
make start-web
# or
cd packages/markitdown-web-ui
uv run python -m markitdown_web_ui
```

Visit `http://localhost:8200` to access the web interface.

### 3. Use MCP Tools

```bash
# Start the MCP server
make start-mcp
# or
cd packages/markitdown-mcp-server
uv run python -m markitdown_mcp_server
```

## 📖 HOW TO Guides

### HOW TO: Use the Web UI

1. **Start the Web UI**:
   ```bash
   make start-web
   ```

2. **Access the Interface**:
   - Open your browser to `http://localhost:8200`
   - Use the drag-and-drop interface to upload files
   - Select output format and click "Convert"

3. **Batch Processing**:
   - Upload multiple files at once
   - Select different output formats for each file
   - Monitor progress in real-time

4. **API Access**:
   ```bash
   # Convert a file via API
   curl -X POST "http://localhost:8200/api/convert" \
        -F "file=@document.pdf" \
        -F "output_format=markdown"
   ```

### HOW TO: Use MCP Tools

1. **Start the MCP Server**:
   ```bash
   make start-mcp
   ```

2. **Configure Claude Desktop**:
   Add to your Claude Desktop configuration:
   ```json
   {
     "mcpServers": {
       "markitdown": {
         "command": "python",
         "args": ["-m", "markitdown_mcp_server"],
         "cwd": "./packages/markitdown-mcp-server"
       }
     }
   }
   ```

3. **Use in Claude Desktop**:
   - Ask Claude to convert files: "Convert this PDF to markdown"
   - Batch process files: "Convert all these documents to markdown"
   - Check supported formats: "What formats does MarkItDown support?"

### HOW TO: Develop Custom Plugins

1. **Create a Plugin**:
   ```bash
   cd packages/markitdown-sample-plugin
   # Follow the example structure
   ```

2. **Install Your Plugin**:
   ```bash
   pip install -e packages/markitdown-sample-plugin
   ```

3. **Use Your Plugin**:
   ```bash
   markitdown --use-plugins --list-plugins
   markitdown --use-plugins document.pdf
   ```

### HOW TO: Deploy to Production

#### Quick Start Deployment
```bash
# Using deployment script (Linux/macOS)
./scripts/deploy.sh

# Using deployment script (Windows)
scripts\deploy.bat

# Manual Docker deployment
docker-compose up -d
```

#### Configurable Directory Deployment
```bash
# Document processing workflow
./scripts/deploy.sh -i /path/to/documents -o /path/to/processed

# Image processing workflow
./scripts/deploy.sh -i /path/to/images -o /path/to/converted -p 8200

# Batch processing workflow
./scripts/deploy.sh -i /batch/input -o /batch/output -p 8300

# Development mode with live reloading
./scripts/deploy.sh -d
```

#### Production Deployment with Nginx
```bash
# Deploy with production profile (includes nginx reverse proxy)
docker-compose --profile production up -d

# Access via:
# - Web UI: http://localhost (nginx proxy)
# - Direct API: http://localhost:8200
# - Health Check: http://localhost/health
```

#### Kubernetes Deployment
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
        - containerPort: 8200
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

#### Environment Configuration
Create a `.env` file for production:
```bash
# Production settings
HOST=0.0.0.0
PORT=8200
DEBUG=false
LOG_LEVEL=WARNING

# Configurable directories
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

#### Monitoring and Maintenance
```bash
# Check application health
curl http://localhost:8200/health

# View application logs
docker-compose logs -f markitdown-web-ui

# Check directory status
curl http://localhost:8200/api/directories/config

# Backup input/output directories
tar -czf backup-$(date +%Y%m%d).tar.gz /path/to/input /path/to/output

# Update the application
git pull
docker-compose down
docker-compose up -d --build
```

## 📖 HOW TO Guides

### HOW TO: Use the Web UI

#### Quick Start
1. **Deploy the application**:
   ```bash
   ./scripts/deploy.sh
   ```

2. **Access the web interface**:
   - Open your browser to `http://localhost:8200`
   - Use the drag-and-drop interface to upload files
   - Select output format and convert

#### API Usage
```bash
# Convert a single file
curl -X POST -F "file=@document.pdf" http://localhost:8200/api/convert

# Batch convert multiple files
curl -X POST -F "files=@file1.pdf" -F "files=@file2.docx" http://localhost:8200/api/convert/batch

# Detect file format
curl -X POST -F "file=@unknown_file" http://localhost:8200/api/detect

# List supported formats
curl http://localhost:8200/api/formats

# Check directory contents
curl http://localhost:8200/api/directories/input
curl http://localhost:8200/api/directories/output
```

### HOW TO: Use MCP Tools

#### Setup MCP Server
```bash
# Install MCP server
pip install -e packages/markitdown-mcp-server

# Start MCP server
python -m markitdown_mcp_server
```

#### Use with Claude Desktop
1. **Configure Claude Desktop**:
   - Add the MCP server to your Claude Desktop configuration
   - Point to the MarkItDown MCP server

2. **Use the tools**:
   - Ask Claude to convert files: "Convert this PDF to markdown"
   - Batch process files: "Convert all these documents to markdown"
   - Check supported formats: "What formats does MarkItDown support?"

#### Direct MCP Tool Usage
```python
from markitdown_mcp_server.tools.convert import ConvertFileTool

# Convert a file
tool = ConvertFileTool()
result = tool.call({
    "input_path": "document.pdf",
    "output_format": "markdown"
})
print(result["data"]["content"])
```

### HOW TO: Configure for Different Use Cases

#### Document Processing Workflow
```bash
# Deploy with document directories
./scripts/deploy.sh -i /shared/documents -o /shared/processed

# Access via web UI to upload and convert documents
# Converted files will be saved to /shared/processed
```

#### Image Processing Workflow
```bash
# Deploy with image directories
./scripts/deploy.sh -i /photos/raw -o /photos/converted -p 8200

# Upload images via web UI
# Get markdown descriptions in /photos/converted
```

#### Batch Processing Workflow
```bash
# Deploy with batch directories
./scripts/deploy.sh -i /batch/input -o /batch/output -p 8300

# Place files in /batch/input
# Process via API or web UI
# Results in /batch/output
```

### HOW TO: Troubleshoot Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :8200

# Use a different port
./scripts/deploy.sh -p 8200
```

#### Permission Denied
```bash
# Fix directory permissions
sudo chown -R $USER:$USER /path/to/input /path/to/output
chmod 755 /path/to/input /path/to/output
```

#### Service Not Starting
```bash
# Check Docker status
docker info

# View application logs
docker-compose logs -f markitdown-web-ui

# Enable debug mode
export DEBUG=true
docker-compose restart markitdown-web-ui
```

#### File Upload Issues
```bash
# Check file size limits
curl -X POST -F "file=@large_file.pdf" http://localhost:8200/api/convert

# Check supported formats
curl http://localhost:8200/api/formats

# Test file format detection
curl -X POST -F "file=@test_file" http://localhost:8200/api/detect
```

## 🔧 Development

### Prerequisites
MarkItDown requires Python 3.10 or higher. It is recommended to use a virtual environment to avoid dependency conflicts.

With the standard Python installation, you can create and activate a virtual environment using the following commands:

```bash
python -m venv .venv
source .venv/bin/activate
```

If using `uv`, you can create a virtual environment with:

```bash
uv venv --python=3.12 .venv
source .venv/bin/activate
# NOTE: Be sure to use 'uv pip install' rather than just 'pip install' to install packages in this virtual environment
```

If you are using Anaconda, you can create a virtual environment with:

```bash
conda create -n markitdown python=3.12
conda activate markitdown
```

### Installation

To install MarkItDown, use pip: `pip install 'markitdown[all]'`. Alternatively, you can install it from the source:

```bash
git clone git@github.com:microsoft/markitdown.git
cd markitdown
pip install -e 'packages/markitdown[all]'
```

### Development Commands

```bash
# Setup development environment
make setup-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Start all services
make start-all

# Clean up
make clean
```

## 📚 Usage

### Command-Line

```bash
markitdown path-to-file.pdf > document.md
```

Or use `-o` to specify the output file:

```bash
markitdown path-to-file.pdf -o document.md
```

You can also pipe content:

```bash
cat path-to-file.pdf | markitdown
```

### Optional Dependencies
MarkItDown has optional dependencies for activating various file formats. Earlier in this document, we installed all optional dependencies with the `[all]` option. However, you can also install them individually for more control. For example:

```bash
pip install 'markitdown[pdf, docx, pptx]'
```

will install only the dependencies for PDF, DOCX, and PPTX files.

At the moment, the following optional dependencies are available:

* `[all]` Installs all optional dependencies
* `[pptx]` Installs dependencies for PowerPoint files
* `[docx]` Installs dependencies for Word files
* `[xlsx]` Installs dependencies for Excel files
* `[xls]` Installs dependencies for older Excel files
* `[pdf]` Installs dependencies for PDF files
* `[outlook]` Installs dependencies for Outlook messages
* `[az-doc-intel]` Installs dependencies for Azure Document Intelligence
* `[audio-transcription]` Installs dependencies for audio transcription of wav and mp3 files
* `[youtube-transcription]` Installs dependencies for fetching YouTube video transcription

### Plugins

MarkItDown also supports 3rd-party plugins. Plugins are disabled by default. To list installed plugins:

```bash
markitdown --list-plugins
```

To enable plugins use:

```bash
markitdown --use-plugins path-to-file.pdf
```

To find available plugins, search GitHub for the hashtag `#markitdown-plugin`. To develop a plugin, see `packages/markitdown-sample-plugin`.

### Azure Document Intelligence

To use Microsoft Document Intelligence for conversion:

```bash
markitdown path-to-file.pdf -o document.md -d -e "<document_intelligence_endpoint>"
```

More information about how to set up an Azure Document Intelligence Resource can be found [here](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/create-document-intelligence-resource?view=doc-intel-4.0.0)

### Python API

Basic usage in Python:

```python
from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
result = md.convert("test.xlsx")
print(result.text_content)
```

Document Intelligence conversion in Python:

```python
from markitdown import MarkItDown

md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")
result = md.convert("test.pdf")
print(result.text_content)
```

To use Large Language Models for image descriptions (currently only for pptx and image files), provide `llm_client` and `llm_model`:

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o", llm_prompt="optional custom prompt")
result = md.convert("example.jpg")
print(result.text_content)
```

### Docker

```sh
docker build -t markitdown:latest .
docker run --rm -i markitdown:latest < ~/your-file.pdf > output.md
```

## 🚀 Deployment Workflows

### File Conversion Workflow
```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant API
    participant MarkItDown
    participant Output
    
    User->>WebUI: Upload file(s)
    WebUI->>API: POST /api/convert
    API->>MarkItDown: Process file
    MarkItDown->>Output: Save to configurable directory
    Output-->>MarkItDown: Success
    MarkItDown-->>API: Return markdown content
    API-->>WebUI: Display results
    WebUI-->>User: Show converted content
```

### MCP Tools Integration
```mermaid
sequenceDiagram
    participant Claude
    participant MCP_Server
    participant MarkItDown
    participant File_System
    
    Claude->>MCP_Server: Request file conversion
    MCP_Server->>MarkItDown: Call convert_file tool
    MarkItDown->>File_System: Read input file
    File_System-->>MarkItDown: File content
    MarkItDown->>MarkItDown: Convert to markdown
    MarkItDown-->>MCP_Server: Return markdown content
    MCP_Server-->>Claude: Display results
```

### Batch Processing Workflow
```mermaid
graph TD
    A[Upload Multiple Files] --> B[Validate Files]
    B --> C{Valid Files?}
    C -->|Yes| D[Process in Parallel]
    C -->|No| E[Return Errors]
    D --> F[Convert Each File]
    F --> G[Save to Output Directory]
    G --> H[Generate Summary]
    H --> I[Return Results]
    E --> I
```

### Deployment Pipeline
```mermaid
graph LR
    A[Source Code] --> B[Build Docker Image]
    B --> C[Run Tests]
    C --> D{Tests Pass?}
    D -->|Yes| E[Deploy to Container]
    D -->|No| F[Fail Build]
    E --> G[Health Check]
    G --> H{Healthy?}
    H -->|Yes| I[Service Ready]
    H -->|No| J[Rollback]
```

## 📖 Documentation

- **[API Documentation](docs/api-documentation.md)**: Complete API reference
- **[Integration Guide](docs/integration-guide.md)**: MCP and FastAPI integration
- **[Deployment Guide](docs/deployment-guide.md)**: Comprehensive deployment instructions
- **[Package Management](docs/package-management.md)**: Development setup and package structure
- **[Tool Cards](docs/tool-cards/)**: Individual MCP tool documentation
- **[Project Plans](docs/plans/)**: Implementation plans and status

## 🤝 Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### How to Contribute

You can help by looking at issues or helping review PRs. Any issue or PR is welcome, but we have also marked some as 'open for contribution' and 'open for reviewing' to help facilitate community contributions. These are of course just suggestions and you are welcome to contribute in any way you like.

<div align="center">

|            | All                                                          | Especially Needs Help from Community                                                                                                      |
| ---------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Issues** | [All Issues](https://github.com/microsoft/markitdown/issues) | [Issues open for contribution](https://github.com/microsoft/markitdown/issues?q=is%3Aissue+is%3Aopen+label%3A%22open+for+contribution%22) |
| **PRs**    | [All PRs](https://github.com/microsoft/markitdown/pulls)     | [PRs open for reviewing](https://github.com/microsoft/markitdown/pulls?q=is%3Apr+is%3Aopen+label%3A%22open+for+reviewing%22)              |

</div>

### Running Tests and Checks

- Navigate to the MarkItDown package:

  ```sh
  cd packages/markitdown
  ```

- Install `hatch` in your environment and run tests:

  ```sh
  pip install hatch  # Other ways of installing hatch: https://hatch.pypa.io/dev/install/
  hatch shell
  hatch test
  ```

  (Alternative) Use the Devcontainer which has all the dependencies installed:

  ```sh
  # Reopen the project in Devcontainer and run:
  hatch test
  ```

- Run pre-commit checks before submitting a PR: `pre-commit run --all-files`

### Contributing 3rd-party Plugins

You can also contribute by creating and sharing 3rd party plugins. See `packages/markitdown-sample-plugin` for more details.

## 🏷️ Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

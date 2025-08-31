# MarkItDown HOW TO Guides

This document provides comprehensive guides for using MarkItDown in various scenarios and environments.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Command Line Interface](#command-line-interface)
3. [Web UI Usage](#web-ui-usage)
4. [MCP Tools Integration](#mcp-tools-integration)
5. [Python API](#python-api)
6. [Plugin Development](#plugin-development)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- UV package manager (recommended)

### Installation

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

### Basic Usage

```bash
# Convert a single file
markitdown document.pdf -o output.md

# Convert with specific format
markitdown presentation.pptx -o slides.md

# List supported formats
markitdown --list-formats
```

## Command Line Interface

### Basic File Conversion

```bash
# Convert PDF to Markdown
markitdown input.pdf -o output.md

# Convert PowerPoint presentation
markitdown slides.pptx -o presentation.md

# Convert Word document
markitdown document.docx -o content.md

# Convert Excel spreadsheet
markitdown data.xlsx -o table.md
```

### Batch Processing

```bash
# Convert multiple files
markitdown file1.pdf file2.docx file3.pptx -o output/

# Convert all files in a directory
markitdown /path/to/documents/ -o converted/

# Convert with different output formats
markitdown file1.pdf -o file1.md file2.docx -o file2.txt
```

### Advanced Options

```bash
# Enable plugins
markitdown --use-plugins document.pdf

# List available plugins
markitdown --list-plugins

# Use Azure Document Intelligence
markitdown document.pdf -d -e "https://your-endpoint.cognitiveservices.azure.com/"

# Verbose output
markitdown document.pdf -v

# Quiet mode
markitdown document.pdf -q
```

### Piping and Streaming

```bash
# Pipe content
cat document.pdf | markitdown > output.md

# Convert from stdin
markitdown < document.pdf > output.md

# Chain with other tools
markitdown document.pdf | grep "important" > important_parts.md
```

## Web UI Usage

### Starting the Web UI

```bash
# Start the web interface
make start-web
# or
cd packages/markitdown-web-ui
uv run python -m markitdown_web_ui
```

### Using the Interface

1. **Access the Web UI**:
   - Open your browser to `http://localhost:8200`
   - You'll see the main conversion interface

2. **Single File Conversion**:
   - Drag and drop a file onto the upload area
   - Select the desired output format
   - Click "Convert"
   - Download the converted file

3. **Batch Processing**:
   - Upload multiple files at once
   - Set different output formats for each file
   - Monitor progress in real-time
   - Download all converted files as a ZIP

4. **API Access**:
   ```bash
   # Convert a file via API
   curl -X POST "http://localhost:8200/api/convert" \
        -F "file=@document.pdf" \
        -F "output_format=markdown"
   
   # Get supported formats
   curl "http://localhost:8200/api/formats"
   
   # Health check
   curl "http://localhost:8200/health"
   ```

### Web UI Features

- **Drag & Drop**: Simple file upload interface
- **Format Detection**: Automatic format detection
- **Progress Tracking**: Real-time conversion progress
- **Error Handling**: Clear error messages
- **Batch Processing**: Convert multiple files simultaneously
- **Download Options**: Individual files or ZIP archive

## MCP Tools Integration

### Setting Up MCP Server

```bash
# Start the MCP server
make start-mcp
# or
cd packages/markitdown-mcp-server
uv run python -m markitdown_mcp_server
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

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

### Using MCP Tools in Claude Desktop

Once configured, you can ask Claude to:

1. **Convert Files**:
   - "Convert this PDF to markdown"
   - "Convert the attached document to text format"

2. **Batch Processing**:
   - "Convert all these documents to markdown"
   - "Process these files and create a summary"

3. **Format Information**:
   - "What formats does MarkItDown support?"
   - "Can MarkItDown handle PowerPoint files?"

4. **Plugin Management**:
   - "List available plugins"
   - "Use plugins to convert this file"

### MCP Tool Examples

```python
# Convert a single file
result = await mcp_client.call_tool("convert_file", {
    "input_path": "/path/to/document.pdf",
    "output_format": "markdown"
})

# Batch conversion
result = await mcp_client.call_tool("convert_batch", {
    "files": [
        {"path": "/path/to/file1.pdf", "output_format": "markdown"},
        {"path": "/path/to/file2.docx", "output_format": "text"}
    ]
})

# Detect format
result = await mcp_client.call_tool("detect_format", {
    "file_path": "/path/to/file"
})

# List supported formats
result = await mcp_client.call_tool("list_supported_formats", {})

# List plugins
result = await mcp_client.call_tool("list_plugins", {})
```

## Python API

### Basic Usage

```python
from markitdown import MarkItDown

# Initialize MarkItDown
md = MarkItDown(enable_plugins=False)

# Convert a file
result = md.convert("document.pdf")
print(result.text_content)
print(result.metadata)
```

### Advanced Configuration

```python
from markitdown import MarkItDown
from openai import OpenAI

# With LLM support for image descriptions
client = OpenAI()
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    llm_prompt="Describe this image in detail"
)

# With Azure Document Intelligence
md = MarkItDown(
    docintel_endpoint="https://your-endpoint.cognitiveservices.azure.com/"
)

# With plugins enabled
md = MarkItDown(enable_plugins=True)
```

### Batch Processing

```python
from markitdown import MarkItDown
from pathlib import Path

md = MarkItDown()

# Convert multiple files
files = ["file1.pdf", "file2.docx", "file3.pptx"]
results = []

for file_path in files:
    result = md.convert(file_path)
    results.append({
        "file": file_path,
        "content": result.text_content,
        "metadata": result.metadata
    })

# Process results
for result in results:
    print(f"Converted {result['file']}: {len(result['content'])} characters")
```

### Error Handling

```python
from markitdown import MarkItDown
from markitdown.exceptions import ConversionError, UnsupportedFormatError

md = MarkItDown()

try:
    result = md.convert("document.pdf")
    print(result.text_content)
except UnsupportedFormatError as e:
    print(f"Unsupported format: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Plugin Development

### Creating a Plugin

1. **Plugin Structure**:
   ```
   my-markitdown-plugin/
   ├── pyproject.toml
   ├── src/
   │   └── my_markitdown_plugin/
   │       ├── __init__.py
   │       └── converter.py
   └── README.md
   ```

2. **Plugin Implementation**:
   ```python
   # src/my_markitdown_plugin/converter.py
   from markitdown.converters.base import DocumentConverter
   from markitdown.models import ConversionResult
   
   class MyCustomConverter(DocumentConverter):
       def __init__(self):
           super().__init__()
           self.supported_formats = [".myformat"]
   
       def convert(self, file_stream, metadata=None):
           # Your conversion logic here
           content = self._convert_my_format(file_stream)
           
           return ConversionResult(
               text_content=content,
               metadata=metadata or {}
           )
   
       def _convert_my_format(self, file_stream):
           # Implement your format conversion
           return "# Converted Content\n\nYour converted content here."
   ```

3. **Plugin Registration**:
   ```python
   # src/my_markitdown_plugin/__init__.py
   from .converter import MyCustomConverter
   
   def register_converters():
       return [MyCustomConverter()]
   ```

4. **Package Configuration**:
   ```toml
   # pyproject.toml
   [project]
   name = "my-markitdown-plugin"
   version = "0.1.0"
   description = "Custom converter for MarkItDown"
   
   [project.entry-points."markitdown.converters"]
   myformat = "my_markitdown_plugin:register_converters"
   ```

### Installing and Using Plugins

```bash
# Install your plugin
pip install -e /path/to/my-markitdown-plugin

# List installed plugins
markitdown --list-plugins

# Use plugins
markitdown --use-plugins document.myformat
```

### Plugin Best Practices

1. **Error Handling**: Always handle errors gracefully
2. **Metadata**: Include relevant metadata in conversion results
3. **Format Detection**: Implement proper format detection
4. **Documentation**: Provide clear documentation for your plugin
5. **Testing**: Include comprehensive tests

## Deployment

### Docker Deployment

1. **Build the Image**:
   ```bash
   docker build -t markitdown:latest .
   ```

2. **Run the Container**:
   ```bash
   # Web UI
   docker run -p 8200:8200 markitdown:latest
   
   # CLI
   docker run --rm -i markitdown:latest < input.pdf > output.md
   
   # With volume mounts
   docker run -v /host/path:/app/data markitdown:latest
   ```

3. **Docker Compose**:
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     markitdown:
       build: .
       ports:
         - "8200:8200"
       volumes:
         - ./uploads:/app/uploads
         - ./outputs:/app/outputs
       environment:
         - MARKITDOWN_HOST=0.0.0.0
         - MARKITDOWN_PORT=8200
   ```

### Systemd Service

1. **Create Service File**:
   ```ini
   # /etc/systemd/system/markitdown.service
   [Unit]
   Description=MarkItDown Web UI
   After=network.target
   
   [Service]
   Type=simple
   User=markitdown
   WorkingDirectory=/opt/markitdown
   ExecStart=/opt/markitdown/.venv/bin/python -m markitdown_web_ui
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start**:
   ```bash
   sudo systemctl enable markitdown
   sudo systemctl start markitdown
   sudo systemctl status markitdown
   ```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/markitdown
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # File upload size limit
    client_max_body_size 100M;
}
```

### Production Considerations

1. **Security**:
   - Use HTTPS
   - Implement authentication
   - Set up rate limiting
   - Configure CORS properly

2. **Performance**:
   - Use a production ASGI server (Gunicorn + Uvicorn)
   - Implement caching
   - Monitor resource usage

3. **Monitoring**:
   - Set up logging
   - Configure health checks
   - Monitor application metrics

4. **Backup**:
   - Regular backups of configuration
   - Database backups if applicable
   - File storage backups

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**:
   ```bash
   # Install packages in editable mode
   cd packages/markitdown-mcp-server
   uv pip install -e .
   
   cd packages/markitdown-web-ui
   uv pip install -e .
   ```

2. **Port Already in Use**:
   ```bash
   # Check what's using the port
   lsof -i :8200
   
   # Kill the process
   kill -9 <PID>
   
   # Or use a different port
   MARKITDOWN_PORT=8101 make start-web
   ```

3. **File Permission Issues**:
   ```bash
   # Fix permissions
   chmod +x scripts/setup-dev.sh
   chmod +x scripts/setup-dev.bat
   ```

4. **Dependency Conflicts**:
   ```bash
   # Clean and reinstall
   make clean
   make setup-dev
   ```

### Debug Mode

```bash
# Enable debug logging
export MARKITDOWN_LOG_LEVEL=DEBUG
make start-web

# Or for MCP server
export MARKITDOWN_LOG_LEVEL=DEBUG
make start-mcp
```

### Getting Help

1. **Check Logs**:
   ```bash
   # Web UI logs
   tail -f logs/markitdown-web.log
   
   # MCP server logs
   tail -f logs/markitdown-mcp.log
   ```

2. **Run Tests**:
   ```bash
   make test
   ```

3. **Check Documentation**:
   - [API Documentation](api-documentation.md)
   - [Integration Guide](integration-guide.md)
   - [Package Management](package-management.md)

4. **Community Support**:
   - GitHub Issues
   - Discussions
   - Stack Overflow

### Performance Optimization

1. **Memory Usage**:
   - Monitor memory usage during large file conversions
   - Implement streaming for large files
   - Use appropriate buffer sizes

2. **CPU Usage**:
   - Implement parallel processing for batch operations
   - Use appropriate worker processes
   - Monitor CPU-intensive operations

3. **Disk I/O**:
   - Use SSD storage for better performance
   - Implement proper file cleanup
   - Monitor disk space usage

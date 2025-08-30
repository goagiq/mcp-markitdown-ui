# MarkItDown Web UI

A FastAPI-based web interface for MarkItDown file conversion tools.

## Overview

This package provides a modern, responsive web interface for converting various file formats to Markdown using the MarkItDown engine. It includes features for single file conversion, batch processing, format detection, and real-time progress tracking.

## Features

- **Modern Web Interface**: Clean, responsive design with drag-and-drop file upload
- **Single File Conversion**: Convert individual files to Markdown
- **Batch Processing**: Convert multiple files simultaneously
- **Format Detection**: Automatically detect file formats and MIME types
- **Real-time Progress**: Track conversion progress in real-time
- **Supported Formats Listing**: View all supported file formats
- **File Validation**: Automatic file type and size validation
- **Background Processing**: Asynchronous file conversion with job tracking

## Installation

```bash
# Install the package
uv pip install markitdown-web-ui

# Or install in development mode
uv pip install -e .
```

## Usage

### Running the Web UI

```bash
# Run the web UI directly
python -m markitdown_web_ui

# Or use the CLI entry point
markitdown-web

# Or run with uvicorn
uvicorn markitdown_web_ui.app:create_app --host 0.0.0.0 --port 8100 --reload
```

### Accessing the Web Interface

Once running, you can access the web interface at:
- **Main Interface**: http://localhost:8100
- **API Documentation**: http://localhost:8100/docs
- **ReDoc Documentation**: http://localhost:8100/redoc
- **Health Check**: http://localhost:8100/health

## API Endpoints

### File Conversion

#### POST /api/convert
Convert a single file to Markdown.

**Request:**
- `file`: Uploaded file
- `output_format`: Output format (default: "markdown")

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "message": "Conversion started",
  "progress": 0
}
```

#### POST /api/convert/batch
Convert multiple files to Markdown.

**Request:**
- `files`: List of uploaded files
- `output_format`: Output format (default: "markdown")

**Response:**
```json
{
  "job_ids": ["uuid1", "uuid2"],
  "status": "processing",
  "message": "Started conversion of 2 files"
}
```

### Format Detection

#### POST /api/detect
Detect the format of a file.

**Request:**
- `file`: Uploaded file

**Response:**
```json
{
  "filename": "document.docx",
  "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "extension": ".docx",
  "size": 12345,
  "supported": true
}
```

### Information

#### GET /api/formats
Get list of supported file formats.

**Response:**
```json
{
  "formats": [
    {
      "extension": ".docx",
      "description": "Files with .docx extension",
      "supported": true
    }
  ],
  "total_formats": 1
}
```

### Job Management

#### GET /api/status/{job_id}
Get the status of a conversion job.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "file_path": "/path/to/file"
}
```

#### GET /api/download/{job_id}
Download a converted file.

**Response:**
```json
{
  "job_id": "uuid",
  "download_url": "/download/uuid",
  "message": "File ready for download"
}
```

## Configuration

The application can be configured using environment variables or a `.env` file:

```env
# Application settings
APP_NAME=MarkItDown Web UI
APP_VERSION=0.1.0
DEBUG=false

# Server settings
HOST=0.0.0.0
PORT=8100

# File upload settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600
ALLOWED_EXTENSIONS=.docx,.pdf,.html,.txt,.md

# MCP Server settings
MCP_SERVER_URL=http://localhost:8001
MCP_SERVER_TIMEOUT=30

# Security settings
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=*
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd packages/markitdown-web-ui

# Create virtual environment
uv venv

# Install dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=markitdown_web_ui

# Run specific test file
pytest tests/test_api.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Architecture

The web UI is built with the following components:

- **FastAPI Application**: Main web framework
- **API Routes**: RESTful API endpoints
- **Static Files**: HTML, CSS, and JavaScript assets
- **Templates**: Jinja2 templates for server-side rendering
- **Utils**: Utility functions for file handling and configuration
- **Models**: Pydantic models for request/response validation

## Dependencies

- `fastapi>=0.104.0`: Web framework
- `uvicorn>=0.24.0`: ASGI server
- `python-multipart>=0.0.6`: File upload handling
- `aiofiles>=23.0.0`: Async file operations
- `jinja2>=3.1.0`: Template engine
- `pydantic>=2.5.0`: Data validation
- `markitdown[all]>=0.1.3`: Core MarkItDown engine
- `markitdown-mcp-server>=0.1.0`: MCP server integration

## License

MIT License - see LICENSE file for details.

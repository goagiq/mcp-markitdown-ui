# MarkItDown API Documentation

## Overview

The MarkItDown API provides both traditional REST endpoints and Model Context Protocol (MCP) tools for file conversion operations. This documentation covers all available endpoints, their request/response schemas, and usage examples.

## Base URLs

- **Web UI**: `http://localhost:8200`
- **API Documentation**: `http://localhost:8200/docs`
- **ReDoc Documentation**: `http://localhost:8200/redoc`
- **Health Check**: `http://localhost:8200/health`

## Authentication

Currently, the API does not require authentication for development use. In production, consider implementing:

- API key authentication
- OAuth 2.0
- JWT tokens

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `FILE_NOT_FOUND` | Requested file does not exist |
| `UNSUPPORTED_FORMAT` | File format not supported |
| `CONVERSION_FAILED` | File conversion failed |
| `INVALID_INPUT` | Invalid request parameters |
| `INTERNAL_ERROR` | Server internal error |

## Core API Endpoints

### Health Check

**GET** `/health`

Check the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "service": "markitdown-web-ui",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Root Information

**GET** `/`

Get basic service information.

**Response:**
```json
{
  "message": "MarkItDown Web UI",
  "version": "1.0.0",
  "description": "FastAPI web UI for MarkItDown file conversion"
}
```

### Web UI Interface

**GET** `/ui`

Serve the web user interface.

**Response:** HTML page with the MarkItDown web interface.

## MCP Tools Endpoints

### MCP Health Check

**GET** `/mcp/health`

Check the health status of the MCP integration.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "markitdown-mcp-integration"
  }
}
```

### List MCP Tools

**GET** `/mcp/tools`

List all available MCP tools.

**Response:**
```json
{
  "success": true,
  "data": {
    "tools": [
      {
        "name": "convert_file",
        "description": "Converts a single file."
      },
      {
        "name": "convert_batch",
        "description": "Converts multiple files."
      },
      {
        "name": "detect_format",
        "description": "Detects file format."
      },
      {
        "name": "list_supported_formats",
        "description": "Lists supported formats."
      },
      {
        "name": "list_plugins",
        "description": "Lists available plugins."
      }
    ]
  }
}
```

### Call MCP Tool

**POST** `/mcp/call`

Call a specific MCP tool with arguments.

**Request Body:**
```json
{
  "tool_name": "convert_file",
  "arguments": {
    "file_path": "/path/to/document.pdf",
    "output_format": "markdown"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "output_path": "/path/to/document.md",
    "status": "success"
  }
}
```

### List Supported Formats

**GET** `/mcp/formats`

List all supported conversion formats.

**Response:**
```json
{
  "success": true,
  "data": {
    "formats": ["markdown", "html", "pdf", "docx", "txt"]
  }
}
```

### List Plugins

**GET** `/mcp/plugins`

List all available MarkItDown plugins.

**Response:**
```json
{
  "success": true,
  "data": {
    "plugins": ["markdown_plugin", "html_plugin"]
  }
}
```

### Detect File Format

**POST** `/mcp/detect`

Detect the format of an uploaded file.

**Request:** Multipart form data with file upload

**Parameters:**
- `file` (file): The file to analyze

**Response:**
```json
{
  "success": true,
  "data": {
    "format": "markdown"
  }
}
```

### Convert Single File

**POST** `/mcp/convert`

Convert a single uploaded file to a specified format.

**Request:** Multipart form data

**Parameters:**
- `file` (file): The file to convert
- `output_format` (string): Target output format

**Response:**
```json
{
  "success": true,
  "data": {
    "output_path": "/tmp/uploads/document.md",
    "status": "success"
  }
}
```

### Convert Multiple Files

**POST** `/mcp/convert/batch`

Convert multiple uploaded files to a specified format.

**Request:** Multipart form data

**Parameters:**
- `files` (array of files): The files to convert
- `output_format` (string): Target output format

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "input_path": "/tmp/uploads/file1.pdf",
        "output_path": "/tmp/uploads/file1.md",
        "status": "success"
      },
      {
        "input_path": "/tmp/uploads/file2.docx",
        "output_path": "/tmp/uploads/file2.md",
        "status": "success"
      }
    ],
    "status": "success"
  }
}
```

## Traditional API Endpoints

### Convert File (REST)

**POST** `/api/convert`

Convert a file using the traditional REST API.

**Request:** Multipart form data

**Parameters:**
- `file` (file): The file to convert
- `output_format` (string, optional): Target output format (default: markdown)
- `options` (string, optional): JSON string with conversion options

**Response:**
```json
{
  "success": true,
  "file_id": "abc123",
  "original_filename": "document.pdf",
  "output_format": "markdown",
  "status": "completed",
  "download_url": "/api/download/abc123"
}
```

### Detect File Format (REST)

**POST** `/api/detect`

Detect the format of an uploaded file.

**Request:** Multipart form data

**Parameters:**
- `file` (file): The file to analyze

**Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "detected_format": "PDF Document",
  "confidence": 0.95,
  "mime_type": "application/pdf"
}
```

### Get Supported Formats (REST)

**GET** `/api/formats`

Get list of supported file formats.

**Response:**
```json
{
  "success": true,
  "formats": [
    {
      "extension": ".pdf",
      "name": "PDF Document",
      "description": "Portable Document Format",
      "supported": true
    },
    {
      "extension": ".docx",
      "name": "Word Document",
      "description": "Microsoft Word Document",
      "supported": true
    }
  ]
}
```

### Get Conversion Status

**GET** `/api/status/{job_id}`

Get the status of a conversion job.

**Response:**
```json
{
  "success": true,
  "job_id": "abc123",
  "status": "completed",
  "progress": 100,
  "result": {
    "output_path": "/path/to/output.md",
    "file_size": 51200
  }
}
```

### Download Converted File

**GET** `/api/download/{file_id}`

Download a converted file.

**Response:** File download with appropriate headers.

## WebSocket Endpoints

### Real-time Updates

**WebSocket** `/ws/updates`

Subscribe to real-time conversion updates.

**Message Format:**
```json
{
  "type": "conversion_update",
  "job_id": "abc123",
  "status": "processing",
  "progress": 75,
  "message": "Converting page 3 of 4"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **MCP endpoints**: 100 requests per minute
- **File uploads**: 10 files per minute
- **General API**: 1000 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234560
```

## File Size Limits

- **Maximum file size**: 100 MB
- **Maximum batch size**: 500 MB total
- **Supported file types**: PDF, DOCX, HTML, TXT, and more

## CORS Configuration

The API supports CORS for web applications:

```javascript
// Example CORS configuration
{
  "origins": ["http://localhost:3000", "https://yourdomain.com"],
  "methods": ["GET", "POST", "PUT", "DELETE"],
  "headers": ["Content-Type", "Authorization"]
}
```

## SDK Examples

### Python Client Example

```python
import requests

# Convert a file
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    data = {'output_format': 'markdown'}
    response = requests.post('http://localhost:8200/mcp/convert', 
                           files=files, data=data)
    result = response.json()
    print(result)

# List supported formats
response = requests.get('http://localhost:8200/mcp/formats')
formats = response.json()
print(formats)
```

### JavaScript Client Example

```javascript
// Convert a file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('output_format', 'markdown');

fetch('http://localhost:8200/mcp/convert', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(result => console.log(result));

// List supported formats
fetch('http://localhost:8200/mcp/formats')
.then(response => response.json())
.then(formats => console.log(formats));
```

### cURL Examples

```bash
# Convert a file
curl -X POST "http://localhost:8200/mcp/convert" \
  -F "file=@document.pdf" \
  -F "output_format=markdown"

# List supported formats
curl -X GET "http://localhost:8200/mcp/formats"

# Detect file format
curl -X POST "http://localhost:8200/mcp/detect" \
  -F "file=@document.pdf"
```

## Troubleshooting

### Common Issues

1. **File not found errors**: Ensure the file path is correct and accessible
2. **Unsupported format**: Check the list of supported formats
3. **Conversion failures**: Verify file integrity and format compatibility
4. **Rate limiting**: Implement exponential backoff for retries

### Debug Mode

Enable debug mode by setting the environment variable:
```bash
export WEB_UI_DEBUG=true
```

This will provide more detailed error messages and logging.

### Logs

Check the application logs for detailed error information:
- **Web UI logs**: `packages/markitdown-web-ui/logs/`
- **MCP Server logs**: `packages/markitdown-mcp-server/logs/`

## Version History

- **v1.0.0**: Initial release with basic conversion capabilities
- **v1.1.0**: Added batch processing and format detection
- **v1.2.0**: Added MCP integration and WebSocket support

## Support

For issues and questions:
- **GitHub Issues**: [https://github.com/microsoft/markitdown/issues](https://github.com/microsoft/markitdown/issues)
- **Documentation**: [https://github.com/microsoft/markitdown#readme](https://github.com/microsoft/markitdown#readme)

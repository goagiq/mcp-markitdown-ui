# MarkItDown MCP Tools and Web UI Technical Specification

## 1. Architecture Overview

### 1.1 System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   FastAPI       │    │   MCP Server    │
│   (Frontend)    │◄──►│   Application   │◄──►│   (Backend)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   MarkItDown    │
                       │   Core Engine   │
                       └─────────────────┘
```

### 1.2 Data Flow
1. User uploads files via Web UI
2. FastAPI receives files and forwards to MCP tools
3. MCP tools process files using MarkItDown engine
4. Results returned through FastAPI to Web UI
5. Real-time updates via WebSocket for file monitoring

## 2. MCP Tools Specification

### 2.1 Tool: `convert_file`
**Purpose**: Convert a single file to Markdown format

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to the file to convert"
    },
    "file_url": {
      "type": "string",
      "description": "URL of the file to convert"
    },
    "output_format": {
      "type": "string",
      "enum": ["markdown", "html", "plain"],
      "default": "markdown",
      "description": "Output format"
    },
    "options": {
      "type": "object",
      "properties": {
        "use_docintel": {
          "type": "boolean",
          "default": false,
          "description": "Use Document Intelligence"
        },
        "endpoint": {
          "type": "string",
          "description": "Document Intelligence endpoint"
        },
        "use_plugins": {
          "type": "boolean",
          "default": false,
          "description": "Use third-party plugins"
        }
      }
    }
  },
  "required": ["file_path"] or ["file_url"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Conversion success status"
    },
    "content": {
      "type": "string",
      "description": "Converted markdown content"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "original_format": {
          "type": "string",
          "description": "Original file format"
        },
        "file_size": {
          "type": "number",
          "description": "File size in bytes"
        },
        "conversion_time": {
          "type": "number",
          "description": "Conversion time in seconds"
        }
      }
    },
    "error": {
      "type": "string",
      "description": "Error message if conversion failed"
    }
  },
  "required": ["success"]
}
```

### 2.2 Tool: `convert_batch`
**Purpose**: Convert multiple files to Markdown format

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "files": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path to the file"
          },
          "file_url": {
            "type": "string",
            "description": "URL of the file"
          }
        }
      },
      "description": "List of files to convert"
    },
    "batch_options": {
      "type": "object",
      "properties": {
        "parallel": {
          "type": "boolean",
          "default": true,
          "description": "Process files in parallel"
        },
        "max_workers": {
          "type": "number",
          "default": 4,
          "description": "Maximum parallel workers"
        }
      }
    }
  },
  "required": ["files"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Original file path"
          },
          "success": {
            "type": "boolean",
            "description": "Conversion success status"
          },
          "content": {
            "type": "string",
            "description": "Converted content"
          },
          "error": {
            "type": "string",
            "description": "Error message if failed"
          }
        }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_files": {
          "type": "number",
          "description": "Total number of files"
        },
        "successful": {
          "type": "number",
          "description": "Number of successful conversions"
        },
        "failed": {
          "type": "number",
          "description": "Number of failed conversions"
        },
        "total_time": {
          "type": "number",
          "description": "Total processing time"
        }
      }
    }
  },
  "required": ["results", "summary"]
}
```

### 2.3 Tool: `detect_format`
**Purpose**: Detect the format of a file

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to the file"
    },
    "file_url": {
      "type": "string",
      "description": "URL of the file"
    }
  },
  "required": ["file_path"] or ["file_url"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "format": {
      "type": "string",
      "description": "Detected file format"
    },
    "mime_type": {
      "type": "string",
      "description": "MIME type"
    },
    "confidence": {
      "type": "number",
      "description": "Detection confidence (0-1)"
    },
    "supported": {
      "type": "boolean",
      "description": "Whether format is supported"
    },
    "metadata": {
      "type": "object",
      "description": "Additional file metadata"
    }
  },
  "required": ["format", "supported"]
}
```

### 2.4 Tool: `list_supported_formats`
**Purpose**: List all supported file formats

**Input Schema**: `{}`

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "formats": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "format": {
            "type": "string",
            "description": "File format name"
          },
          "extensions": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "File extensions"
          },
          "mime_types": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "MIME types"
          },
          "description": {
            "type": "string",
            "description": "Format description"
          }
        }
      }
    }
  },
  "required": ["formats"]
}
```

### 2.5 Tool: `list_plugins`
**Purpose**: List available plugins

**Input Schema**: `{}`

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "plugins": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Plugin name"
          },
          "version": {
            "type": "string",
            "description": "Plugin version"
          },
          "description": {
            "type": "string",
            "description": "Plugin description"
          },
          "formats": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Supported formats"
          }
        }
      }
    }
  },
  "required": ["plugins"]
}
```

## 3. FastAPI Endpoints Specification

### 3.1 File Conversion Endpoints

#### POST `/api/convert`
**Purpose**: Convert uploaded files to Markdown

**Request**:
- Content-Type: `multipart/form-data`
- Body: File uploads with optional parameters

**Response**:
```json
{
  "job_id": "string",
  "status": "processing|completed|failed",
  "results": [
    {
      "filename": "string",
      "success": "boolean",
      "content": "string",
      "error": "string"
    }
  ]
}
```

#### GET `/api/status/{job_id}`
**Purpose**: Get conversion job status

**Response**:
```json
{
  "job_id": "string",
  "status": "processing|completed|failed",
  "progress": "number",
  "results": "array"
}
```

### 3.2 Format Detection Endpoints

#### POST `/api/detect`
**Purpose**: Detect format of uploaded files

**Request**: File uploads
**Response**: Array of format detection results

### 3.3 Information Endpoints

#### GET `/api/formats`
**Purpose**: Get supported formats

#### GET `/api/plugins`
**Purpose**: Get available plugins

### 3.4 MCP Integration Endpoints

#### POST `/mcp/convert`
**Purpose**: MCP tool endpoint for file conversion
**Operation ID**: `markitdown_convert_file`

#### POST `/mcp/batch`
**Purpose**: MCP tool endpoint for batch conversion
**Operation ID**: `markitdown_convert_batch`

#### POST `/mcp/detect`
**Purpose**: MCP tool endpoint for format detection
**Operation ID**: `markitdown_detect_format`

#### GET `/mcp/formats`
**Purpose**: MCP tool endpoint for supported formats
**Operation ID**: `markitdown_list_formats`

#### GET `/mcp/plugins`
**Purpose**: MCP tool endpoint for plugins
**Operation ID**: `markitdown_list_plugins`

## 4. WebSocket Events

### 4.1 File Monitoring Events

#### `file_added`
```json
{
  "event": "file_added",
  "data": {
    "file_path": "string",
    "timestamp": "string"
  }
}
```

#### `file_modified`
```json
{
  "event": "file_modified",
  "data": {
    "file_path": "string",
    "timestamp": "string"
  }
}
```

#### `conversion_progress`
```json
{
  "event": "conversion_progress",
  "data": {
    "job_id": "string",
    "progress": "number",
    "current_file": "string"
  }
}
```

## 5. Package Structure

### 5.1 markitdown-mcp-server
```
markitdown-mcp-server/
├── pyproject.toml
├── src/
│   └── markitdown_mcp_server/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── convert.py
│       │   ├── detect.py
│       │   └── info.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
└── tests/
    └── test_tools.py
```

### 5.2 markitdown-web-ui
```
markitdown-web-ui/
├── pyproject.toml
├── src/
│   └── markitdown_web_ui/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── convert.py
│       │   ├── detect.py
│       │   └── info.py
│       ├── static/
│       │   ├── css/
│       │   ├── js/
│       │   └── index.html
│       └── websocket/
│           ├── __init__.py
│           └── file_monitor.py
└── tests/
    └── test_api.py
```

## 6. Dependencies

### 6.1 Core Dependencies
```toml
dependencies = [
    "fastapi>=0.104.0",
    "fastapi-mcp>=1.0.0",
    "uvicorn>=0.24.0",
    "python-multipart>=0.0.6",
    "websockets>=12.0",
    "watchdog>=3.0.0",
    "pydantic>=2.5.0",
    "markitdown[all]>=1.0.0"
]
```

### 6.2 Development Dependencies
```toml
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0"
]
```

## 7. Configuration

### 7.1 Environment Variables
```bash
# Server Configuration
MARKITDOWN_HOST=0.0.0.0
MARKITDOWN_PORT=8000
MARKITDOWN_WORKERS=4

# File Upload Configuration
MAX_FILE_SIZE=100MB
UPLOAD_DIR=/tmp/markitdown

# MCP Configuration
MCP_ENABLE=true
MCP_TOOLS_PATH=/path/to/tools

# Monitoring Configuration
FILE_MONITOR_ENABLE=true
FILE_MONITOR_PATH=/path/to/watch
```

### 7.2 Configuration File
```yaml
# config.yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4

upload:
  max_size: 100MB
  directory: /tmp/markitdown

mcp:
  enabled: true
  tools_path: /path/to/tools

monitoring:
  enabled: true
  watch_path: /path/to/watch
  events: [created, modified, deleted]
```

## 8. Error Handling

### 8.1 Error Codes
- `400`: Bad Request - Invalid input
- `413`: Payload Too Large - File too big
- `415`: Unsupported Media Type - Unsupported format
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Conversion failed
- `503`: Service Unavailable - Service overloaded

### 8.2 Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object"
  }
}
```

## 9. Security Considerations

### 9.1 File Upload Security
- File size limits
- File type validation
- Virus scanning (optional)
- Temporary file cleanup

### 9.2 API Security
- Rate limiting
- Input validation
- CORS configuration
- Authentication (future)

### 9.3 Data Privacy
- No file content logging
- Temporary file storage only
- Secure file deletion

## 10. Performance Considerations

### 10.1 Optimization Strategies
- Async file processing
- Parallel batch processing
- File streaming for large files
- Caching of format detection results

### 10.2 Resource Management
- Memory usage monitoring
- CPU usage optimization
- Disk I/O optimization
- Connection pooling

## 11. Monitoring and Logging

### 11.1 Metrics
- Conversion success rate
- Processing time
- File size distribution
- Error rates by format

### 11.2 Logging
- Request/response logging
- Error logging with stack traces
- Performance metrics
- Security events

## 12. Testing Strategy

### 12.1 Unit Tests
- Individual tool functionality
- Input validation
- Error handling
- Edge cases

### 12.2 Integration Tests
- End-to-end workflows
- API endpoint testing
- MCP tool integration
- File processing pipelines

### 12.3 Performance Tests
- Load testing
- Stress testing
- Memory leak detection
- Response time validation

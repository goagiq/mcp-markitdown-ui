# MCP (Model Context Protocol) Implementation Guide

## Overview

This guide documents the implementation of a Model Context Protocol (MCP) server for MarkItDown using FastAPI-MCP with Streamable HTTP transport. The MCP server exposes document conversion capabilities as tools that can be used by MCP clients like Cursor.

## Architecture

```
┌─────────────────┐    HTTP/JSON-RPC    ┌─────────────────┐
│   MCP Client    │ ◄─────────────────► │  MarkItDown     │
│   (e.g., Cursor)│                     │  MCP Server     │
└─────────────────┘                     └─────────────────┘
                                              │
                                              ▼
                                       ┌─────────────────┐
                                       │  MarkItDown     │
                                       │  Core Library   │
                                       └─────────────────┘
```

## Key Components

### 1. `main.py` - MCP Server Entry Point
- Configures FastAPI-MCP with Streamable HTTP transport
- Mounts MCP operations to FastAPI app
- Starts the server with uvicorn

### 2. `deployment.py` - FastAPI Application
- Defines REST API endpoints with `operation_id` decorators
- Contains Pydantic models for request/response
- Integrates with MarkItDown core library

### 3. FastAPI-MCP Integration
- Automatically generates MCP tools from FastAPI endpoints
- Handles MCP protocol communication
- Manages session management for Streamable HTTP

## Implementation Steps

### Step 1: Install Dependencies

```bash
# Install FastAPI-MCP and required packages
pip install fastapi-mcp fastapi uvicorn pydantic python-multipart
```

### Step 2: Create FastAPI Application (`deployment.py`)

```python
#!/usr/bin/env python3
"""
FastAPI deployment for MarkItDown MCP Server
Provides REST API access to MCP tools
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

# Add the packages directory to the path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                'packages/markitdown/src'))

from markitdown import MarkItDown

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MarkItDown MCP Server",
    description="Model Context Protocol Server for document conversion",
    version="1.0.0"
)

# Initialize MarkItDown
markitdown = MarkItDown()

# Pydantic models for request/response
class ConvertRequest(BaseModel):
    file_path: Optional[str] = None
    file_content: Optional[str] = None
    file_name: Optional[str] = None

class ConvertResponse(BaseModel):
    success: bool
    markdown: str
    text_length: int
    error: Optional[str] = None

class FormatDetectionRequest(BaseModel):
    file_path: Optional[str] = None
    file_content: Optional[str] = None

class FormatDetectionResponse(BaseModel):
    format: str
    error: Optional[str] = None

class SupportedFormatsResponse(BaseModel):
    formats: list[str]

# FastAPI endpoints with operation_id decorators
@app.get("/", operation_id="get_root")
async def root():
    """Root endpoint"""
    return {
        "service": "MarkItDown MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "convert": "/convert",
            "detect_format": "/detect_format",
            "supported_formats": "/supported_formats",
            "health": "/health"
        }
    }

@app.get("/health", operation_id="get_health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "markitdown-mcp",
        "version": "1.0.0"
    }

@app.post("/convert", operation_id="convert_document")
async def convert_document(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None),
    file_name: Optional[str] = Form(None)
):
    """Convert a document to markdown format"""
    # Implementation details...
    pass

@app.post("/detect_format", operation_id="detect_format")
async def detect_format(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None)
):
    """Detect the format of a document"""
    # Implementation details...
    pass

@app.get("/supported_formats", operation_id="list_supported_formats")
async def list_supported_formats():
    """List all supported document formats"""
    # Implementation details...
    pass
```

### Step 3: Create MCP Server Entry Point (`main.py`)

```python
#!/usr/bin/env python3
"""
MCP Server for MarkItDown - Model Context Protocol Server
Provides document conversion capabilities through MCP protocol
"""

from deployment import app
from fastapi_mcp import FastApiMCP
import uvicorn


def main():
    # Create FastApiMCP instance with operation IDs
    mcp = FastApiMCP(
        app, 
        include_operations=[
            "convert_document",
            "list_supported_formats",
            "detect_format",
            "get_root",
            "get_health"
        ]
    )
    
    # Mount the MCP operations to the FastAPI app using HTTP transport (recommended)
    mcp.mount_http(mount_path="/mcp")
    
    # Run the FastAPI server with uvicorn
    port = 8200  # Explicitly set to 8200
    host = "127.0.0.1"  # Explicitly set to 127.0.0.1
    print(f"Starting server on {host}:{port}")
    print(f"MCP endpoint available at: http://{host}:{port}/mcp")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
```

### Step 4: Start the MCP Server

```bash
# Start the server
python main.py

# Wait 30 seconds for full initialization
# The server will be available at http://127.0.0.1:8200/mcp
```

## MCP Protocol Details

### Streamable HTTP Transport

The implementation uses **Streamable HTTP transport**, which is the recommended approach according to the [FastAPI-MCP documentation](https://fastapi-mcp.tadata.com/advanced/transport#http-transport-recommended).

#### Key Requirements:

1. **Endpoint**: `/mcp`
2. **Headers**: `Accept: application/json, text/event-stream`
3. **Session Management**: Requires session establishment via GET request
4. **Content-Type**: `application/json` for POST requests

#### Protocol Flow:

1. **Session Establishment**:
   ```http
   GET /mcp HTTP/1.1
   Accept: text/event-stream
   ```
   Response includes: `mcp-session-id: <session-id>`

2. **Tool Operations**:
   ```http
   POST /mcp HTTP/1.1
   Content-Type: application/json
   Accept: application/json, text/event-stream
   MCP-Session-ID: <session-id>
   
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/list"
   }
   ```

### Available MCP Tools

The server automatically exposes the following tools based on the `operation_id` decorators:

1. **`convert_document`**
   - **Description**: Convert a document to markdown format
   - **Parameters**:
     - `file_path` (string): Path to the document file to convert
     - `file_content` (string): Base64 encoded file content
     - `file_name` (string): Name of the file (required if using file_content)

2. **`list_supported_formats`**
   - **Description**: List all supported document formats
   - **Parameters**: None

3. **`detect_format`**
   - **Description**: Detect the format of a document
   - **Parameters**:
     - `file_path` (string): Path to the document file
     - `file_content` (string): Base64 encoded file content

## Testing the MCP Server

### 1. Health Check

```bash
curl http://127.0.0.1:8200/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "markitdown-mcp",
  "version": "1.0.0"
}
```

### 2. REST API Endpoints

```bash
# List supported formats
curl http://127.0.0.1:8200/supported_formats

# Convert document (using file path)
curl -X POST http://127.0.0.1:8200/convert \
  -F "file_path=/path/to/document.pdf"

# Detect format
curl -X POST http://127.0.0.1:8200/detect_format \
  -F "file_path=/path/to/document.pdf"
```

### 3. MCP Protocol Testing

Use the provided test client:

```bash
python simple_mcp_client.py
```

Or test manually:

```bash
# Step 1: Establish session
curl -H "Accept: text/event-stream" http://127.0.0.1:8200/mcp

# Step 2: List tools (using session ID from step 1)
curl -X POST http://127.0.0.1:8200/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Session-ID: <session-id>" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## Client Configuration

### Cursor MCP Client Configuration

To configure Cursor to use the MarkItDown MCP server:

1. **Endpoint**: `http://127.0.0.1:8200/mcp`
2. **Transport**: Streamable HTTP
3. **Headers**: 
   - `Accept: application/json, text/event-stream`
   - `Content-Type: application/json`

### Example Client Configuration

```json
{
  "mcpServers": {
    "markitdown": {
      "url": "http://127.0.0.1:8200/mcp",
      "transport": "http"
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **400 Bad Request - Missing session ID**
   - **Cause**: POST request without establishing session first
   - **Solution**: Always establish session with GET request first

2. **406 Not Acceptable**
   - **Cause**: Missing required Accept headers
   - **Solution**: Include `Accept: application/json, text/event-stream`

3. **405 Method Not Allowed**
   - **Cause**: Using wrong HTTP method
   - **Solution**: Use GET for session establishment, POST for operations

4. **Port Already in Use**
   - **Cause**: Another process using port 8200
   - **Solution**: Kill existing process or change port

### Debug Commands

```bash
# Check if server is running
curl http://127.0.0.1:8200/health

# Check port usage
netstat -ano | findstr :8200

# Kill process using port
taskkill //PID <PID> //F
```

## File Structure

```
markitdown/
├── main.py                    # MCP server entry point
├── deployment.py              # FastAPI application
├── simple_mcp_client.py       # Test client
├── test_mcp_client.py         # Debug client
├── requirements-mcp.txt       # MCP dependencies
└── docs/
    └── mcp-implementation-guide.md  # This guide
```

## Dependencies

### Required Packages

```
fastapi-mcp>=1.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
```

### Installation

```bash
pip install -r requirements-mcp.txt
```

## Best Practices

1. **Always use `operation_id` decorators** on FastAPI endpoints
2. **Wait 30 seconds** after server start for full initialization
3. **Use proper session management** for Streamable HTTP transport
4. **Include required headers** in all MCP requests
5. **Test with provided client** before configuring production clients
6. **Monitor server logs** for debugging information

## References

- [FastAPI-MCP Documentation](https://fastapi-mcp.tadata.com/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamable HTTP Transport Guide](https://fastapi-mcp.tadata.com/advanced/transport#http-transport-recommended)

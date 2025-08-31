# MarkItDown MCP Server

This directory contains the Model Context Protocol (MCP) server implementation for MarkItDown, providing document conversion capabilities through both MCP protocol and REST API endpoints.

## Files

- `main.py` - MCP server implementation using stdio protocol
- `deployment.py` - FastAPI server with MCP protocol and REST API endpoints
- `requirements-mcp.txt` - Dependencies for the MCP server
- `test_mcp_server.py` - Test script to verify server functionality

## Features

### MCP Tools

1. **convert_document** - Convert a document to markdown format
   - Parameters:
     - `file_path` (string): Path to the document file to convert
     - `file_content` (string): Base64 encoded file content (alternative to file_path)
     - `file_name` (string): Name of the file (required if using file_content)

2. **list_supported_formats** - List all supported document formats
   - No parameters required

3. **detect_format** - Detect the format of a document
   - Parameters:
     - `file_path` (string): Path to the document file
     - `file_content` (string): Base64 encoded file content

### Supported Formats

- PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS
- TXT, MD, HTML, HTM, EPUB, CSV, ZIP

## Installation

1. Install the MCP server dependencies:
```bash
pip install -r requirements-mcp.txt
```

2. Ensure the MarkItDown package is available in the `packages/` directory.

## Usage

### Running the MCP Server

#### Option 1: FastAPI Server (Recommended)
```bash
python deployment.py
```

This starts the server on `127.0.0.1:8200` with both MCP protocol and REST API endpoints.

#### Option 2: Stdio MCP Server
```bash
python main.py
```

This runs the MCP server using stdio protocol for direct integration with MCP clients.

### REST API Endpoints

- `GET /` - Root endpoint with service information
- `GET /health` - Health check endpoint
- `POST /convert` - Convert document to markdown
- `POST /detect_format` - Detect document format
- `GET /supported_formats` - List supported formats
- `POST /mcp` - MCP protocol endpoint

### MCP Protocol Endpoint

The MCP protocol is accessible at `127.0.0.1:8200/mcp` and supports:

- `tools/list` - List available tools
- `tools/call` - Call a specific tool

## Testing

Run the test script to verify the server functionality:

```bash
python test_mcp_server.py
```

This will:
1. Start the MCP server
2. Test REST API endpoints
3. Test MCP protocol endpoints
4. Stop the server

## Example Usage

### REST API Example

```bash
# Health check
curl http://127.0.0.1:8200/health

# List supported formats
curl http://127.0.0.1:8200/supported_formats

# Convert a document
curl -X POST http://127.0.0.1:8200/convert \
  -F "file=@document.pdf"
```

### MCP Protocol Example

```bash
# List available tools
curl -X POST http://127.0.0.1:8200/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'

# Call list_supported_formats tool
curl -X POST http://127.0.0.1:8200/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_supported_formats",
      "arguments": {}
    }
  }'
```

## Configuration

The server can be configured using environment variables:

- `PORT` - Server port (default: 8200)
- `HOST` - Server host (default: 127.0.0.1)

## Integration

### With MCP Clients

The server can be integrated with MCP clients by configuring the server to use the stdio protocol:

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "python",
      "args": ["/path/to/markitdown/main.py"]
    }
  }
}
```

### With REST API Clients

Any HTTP client can interact with the REST API endpoints for document conversion and format detection.

## Troubleshooting

1. **Port already in use**: Change the port using the `PORT` environment variable
2. **Import errors**: Ensure all dependencies are installed and the MarkItDown package is available
3. **File not found**: Check that file paths are correct and files exist
4. **Permission errors**: Ensure the server has read access to input files and write access to output directories

## Development

To modify the MCP server:

1. Edit `main.py` for stdio protocol changes
2. Edit `deployment.py` for FastAPI/REST API changes
3. Update `requirements-mcp.txt` for dependency changes
4. Run tests with `test_mcp_server.py`

## License

This MCP server implementation is part of the MarkItDown project and follows the same license terms.

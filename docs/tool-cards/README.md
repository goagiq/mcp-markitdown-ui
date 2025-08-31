# MarkItDown MCP Tools

This directory contains tool cards for all available MCP (Model Context Protocol) tools in the MarkItDown server.

## Available Tools

### Core Conversion Tools

| Tool | File | Description |
|------|------|-------------|
| `convert_document` | [convert_document_tool.md](./convert_document_tool.md) | Converts various document formats to markdown |
| `detect_format` | [detect_format_tool.md](./detect_format_tool.md) | Detects document format by file extension |

### Information Tools

| Tool | File | Description |
|------|------|-------------|
| `list_supported_formats` | [list_supported_formats_tool.md](./list_supported_formats_tool.md) | Lists all supported document formats |
| `get_root` | [get_root_tool.md](./get_root_tool.md) | Provides server information and endpoint list |
| `get_health` | [get_health_tool.md](./get_health_tool.md) | Returns server health status |

## Tool Categories

### 🔄 **Document Processing**
- **convert_document**: Main conversion tool supporting multiple input methods
- **detect_format**: Format detection for validation and compatibility checking

### ℹ️ **Information & Discovery**
- **list_supported_formats**: Discover available formats
- **get_root**: Server information and endpoint discovery
- **get_health**: Health monitoring and status checks

## MCP Protocol Integration

All tools are exposed through the FastAPI-MCP integration at:
- **Endpoint**: `http://127.0.0.1:8200/mcp`
- **Transport**: Streamable HTTP
- **Protocol**: JSON-RPC 2.0

## Usage Examples

### List Available Tools
```bash
curl -X POST http://127.0.0.1:8200/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Session-ID: <session-id>" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

### Convert Document
```bash
curl -X POST http://127.0.0.1:8200/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Session-ID: <session-id>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "convert_document",
      "arguments": {
        "file_path": "/path/to/document.pdf"
      }
    }
  }'
```

## Tool Card Format

Each tool card follows the standard template format and includes:

- **General Info**: Name, version, author, description
- **Required Libraries**: Dependencies and imports
- **Intended Use**: Purpose and use cases
- **Input/Output Schemas**: JSON schema definitions
- **Examples**: Usage examples with input/output
- **Safety & Reliability**: Security and reliability considerations

## Related Documentation

- [MCP Implementation Guide](../mcp-implementation-guide.md)
- [MCP Quick Reference](../mcp-quick-reference.md)
- [API Documentation](../api-documentation.md)

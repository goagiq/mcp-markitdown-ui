# MCP Quick Reference Card

## Server Configuration

### Endpoints
- **Web UI**: `http://127.0.0.1:8200/` (redirects to `/web`)
- **Web UI Direct**: `http://127.0.0.1:8200/web`
- **MCP Server**: `http://127.0.0.1:8200/mcp`
- **Health Check**: `http://127.0.0.1:8200/health`
- **Port**: 8200

### Required Headers (MCP)
```
Accept: application/json, text/event-stream
Content-Type: application/json
MCP-Session-ID: <session-id>
```

## Implementation Patterns

### ❌ Official Documentation Pattern (Problematic)
```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# Your API app
api_app = FastAPI()
# ... define your API endpoints on api_app ...

# A separate app for the MCP server
mcp_app = FastAPI()

# Create MCP server from the API app
mcp = FastApiMCP(api_app)

# Mount the MCP server to the separate app
mcp.mount_http(mcp_app)
```

**Issues with this approach:**
- Requires running two separate FastAPI apps
- More complex setup and routing
- Potential port conflicts
- Harder to manage in production

### ✅ Working Pattern (What We Implemented)
```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# Create the main FastAPI app
app = FastAPI()

# Create and mount the web UI
web_app = create_web_app()
app.mount("/web", web_app)

# Add redirect from root to web UI
@app.get("/")
async def root():
    return RedirectResponse(url="/web")

# Create MCP server from separate app
mcp = FastApiMCP(mcp_app, include_operations=[
    "convert_document", 
    "get_health"
])

# Mount MCP to the main app
mcp.mount_http(app, mount_path="/mcp")

# Run combined server
uvicorn.run(app, host="127.0.0.1", port=8200)
```

**Advantages of this approach:**
- Single server with multiple capabilities
- Web UI + MCP server in one process
- No port conflicts
- Easier deployment and management

## Quick Start

### 1. Start Server
```bash
python main.py
# Wait 30 seconds for initialization
```

### 2. Test Health
```bash
curl http://127.0.0.1:8200/health
```

### 3. Access Web UI
```bash
# Open in browser: http://127.0.0.1:8200
# Or directly: http://127.0.0.1:8200/web
```

### 4. Test MCP Client
```bash
python simple_mcp_client.py
```

## Available Tools

### MCP Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `convert_document` | Convert document to markdown | `file_path`, `file_content`, `file_name` |
| `list_supported_formats` | List supported formats | None |
| `detect_format` | Detect document format | `file_path`, `file_content` |

### Web UI Features
- **Multiple file upload** with drag & drop
- **Bulk conversion** processing
- **Real-time progress** tracking
- **File validation** and error handling
- **Download converted** markdown files

## Protocol Flow

1. **Establish Session**
   ```http
   GET /mcp HTTP/1.1
   Accept: text/event-stream
   ```

2. **List Tools**
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

3. **Call Tool**
   ```http
   POST /mcp HTTP/1.1
   Content-Type: application/json
   Accept: application/json, text/event-stream
   MCP-Session-ID: <session-id>
   
   {
     "jsonrpc": "2.0",
     "id": 2,
     "method": "tools/call",
     "params": {
       "name": "convert_document",
       "arguments": {
         "file_path": "/path/to/file.pdf"
       }
     }
   }
   ```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Missing session ID | Establish session with GET first |
| 406 Not Acceptable | Missing Accept headers | Include `Accept: application/json, text/event-stream` |
| 405 Method Not Allowed | Wrong HTTP method | Use GET for session, POST for operations |
| Port in use | Another process on 8200 | Kill process or change port |
| Import errors | Wrong implementation pattern | Use single app pattern (see above) |
| MCP tools not found | Missing operation_id decorators | Add `operation_id` to all endpoints |
| Server won't start | Multiple FastAPI apps | Use single app with `mount_path` |

## Key Files

- `main.py` - Combined server entry point (Web UI + MCP)
- `deployment.py` - MCP FastAPI application
- `packages/markitdown-web-ui/src/markitdown_web_ui/app.py` - Web UI application
- `simple_mcp_client.py` - MCP test client
- `requirements-mcp.txt` - Dependencies

## Why We Had Trouble Initially

The official FastAPI-MCP documentation shows a pattern with two separate FastAPI apps, but this approach:
1. **Creates complexity** - Managing two apps instead of one
2. **Causes confusion** - Which app to run, which port to use
3. **Leads to errors** - Port conflicts, routing issues
4. **Harder to debug** - More moving parts

Our working solution uses a **combined server approach** with:
- ✅ **Single server** - Web UI + MCP in one process
- ✅ **Multiple capabilities** - Both web interface and MCP protocol
- ✅ **No conflicts** - Proper mounting and routing
- ✅ **Easier deployment** - One process to manage
- ✅ **Better user experience** - Web UI for humans, MCP for AI clients

## Client Configuration

### Cursor
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

## Debug Commands

```bash
# Check server status
curl http://127.0.0.1:8200/health

# Check port usage
netstat -ano | findstr :8200

# Kill process
taskkill //PID <PID> //F

# Test MCP endpoint
python simple_mcp_client.py

# Test web UI
curl -L http://127.0.0.1:8200/

# Test web UI direct
curl http://127.0.0.1:8200/web
```

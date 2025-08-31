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

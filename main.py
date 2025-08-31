#!/usr/bin/env python3
"""
MarkItDown Server - Web UI + MCP Server
Provides both web interface and MCP protocol capabilities
"""

import os
import sys
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_mcp import FastApiMCP
import uvicorn

# Add the packages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                'packages/markitdown-web-ui/src'))

from deployment import app as mcp_app
from markitdown_web_ui.app import create_app as create_web_app


def main():
    # Create the main FastAPI app
    app = FastAPI(
        title="MarkItDown Server",
        description="Web UI and MCP Server for document conversion",
        version="1.0.0"
    )
    
    # Create and mount the web UI
    web_app = create_web_app()
    
    # Mount web UI routes to the main app at /web
    app.mount("/web", web_app)
    
    # Mount REST API endpoints from deployment.py
    app.mount("/api", mcp_app)
    
    # Add redirect from root to web UI
    @app.get("/")
    async def root():
        return RedirectResponse(url="/web")
    
    # Create FastApiMCP instance - try without include_operations
    mcp = FastApiMCP(mcp_app)
    
    # Mount the MCP operations to the main app using HTTP transport
    mcp.mount_http(app, mount_path="/mcp")
    
    # Run the combined server with uvicorn
    port = int(os.environ.get('PORT', 8200))
    host = os.environ.get('HOST', '0.0.0.0')  # Use 0.0.0.0 for Docker
    print(f"Starting MarkItDown Server on {host}:{port}")
    print(f"Web UI available at: http://{host}:{port}/web")
    print(f"REST API available at: http://{host}:{port}/api")
    print(f"MCP endpoint available at: http://{host}:{port}/mcp")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

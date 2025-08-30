"""Main FastAPI application for MarkItDown Web UI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .api.routes import api_router
from .mcp_integration import mcp_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="MarkItDown Web UI",
        description="Web interface for MarkItDown file conversion",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount(
            "/static", 
            StaticFiles(directory=str(static_path)), 
            name="static"
        )
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Include MCP routes
    app.include_router(mcp_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "markitdown-web-ui"}
    
    # Root endpoint - serve the web UI
    @app.get("/")
    async def root():
        """Serve the web UI at root endpoint."""
        static_path = Path(__file__).parent / "static" / "index.html"
        if static_path.exists():
            from fastapi.responses import FileResponse
            return FileResponse(static_path)
        else:
            return {"message": "Web UI not found", "docs": "/docs"}
    
    # API info endpoint
    @app.get("/api")
    async def api_info():
        """API information endpoint."""
        return {"message": "MarkItDown Web UI", "version": "0.1.0"}
    
    return app

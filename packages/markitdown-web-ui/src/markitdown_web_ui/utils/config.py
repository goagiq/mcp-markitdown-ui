"""Configuration settings for MarkItDown Web UI."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    app_name: str = "MarkItDown Web UI"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8100
    
    # File upload settings
    upload_dir: Path = Path("uploads")
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: list[str] = [
        ".docx", ".pdf", ".html", ".txt", ".md", ".rtf",
        ".odt", ".epub", ".csv", ".xlsx", ".pptx", ".jpg",
        ".png", ".gif", ".mp3", ".wav", ".mp4", ".avi"
    ]
    
    # Input/Output directory configuration
    input_dir: Path = Path("/app/input")
    output_dir: Path = Path("/app/output")
    
    # Alternative directory configurations for different use cases
    # These can be overridden via environment variables
    # For document processing: INPUT_DIR=/path/to/documents, 
    # OUTPUT_DIR=/path/to/processed
    # For image processing: INPUT_DIR=/path/to/images, 
    # OUTPUT_DIR=/path/to/converted
    # For batch processing: INPUT_DIR=/path/to/batch/input, 
    # OUTPUT_DIR=/path/to/batch/output
    
    # MCP Server settings
    mcp_server_url: Optional[str] = None
    mcp_server_timeout: int = 30
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    cors_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

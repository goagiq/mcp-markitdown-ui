"""Validation utilities for MarkItDown MCP Server."""

import os
from pathlib import Path
from typing import Union
from urllib.parse import urlparse


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """Validate if a file path exists and is accessible."""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def validate_url(url: str) -> bool:
    """Validate if a URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_file_size(file_path: Union[str, Path], max_size_mb: int = 100) -> bool:
    """Validate if a file size is within limits."""
    try:
        path = Path(file_path)
        if not path.exists():
            return False
        
        size_mb = path.stat().st_size / (1024 * 1024)
        return size_mb <= max_size_mb
    except Exception:
        return False

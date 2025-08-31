"""
URI utility functions.
"""

from urllib.parse import urlparse, unquote
from pathlib import Path


def parse_data_uri(uri: str) -> tuple[bytes, str]:
    """Parse a data URI and return the data and MIME type."""
    if not uri.startswith('data:'):
        raise ValueError("Not a data URI")
    
    # Split on first comma
    header, data = uri.split(',', 1)
    
    # Parse the header
    parts = header[5:].split(';')
    mime_type = parts[0] if parts[0] else 'text/plain'
    
    # Handle base64 encoding
    if 'base64' in parts:
        import base64
        return base64.b64decode(data), mime_type
    else:
        return unquote(data).encode('utf-8'), mime_type


def file_uri_to_path(uri: str) -> Path:
    """Convert a file URI to a file path."""
    if not uri.startswith('file://'):
        raise ValueError("Not a file URI")
    
    parsed = urlparse(uri)
    return Path(unquote(parsed.path))


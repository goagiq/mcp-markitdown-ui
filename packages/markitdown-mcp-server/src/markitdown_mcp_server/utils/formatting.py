"""Formatting utilities for MarkItDown MCP Server."""

import json
from typing import Any, Dict


def format_response(data: Any, success: bool = True) -> Dict[str, Any]:
    """Format a successful response."""
    return {
        "success": success,
        "data": data,
        "timestamp": "2024-01-01T00:00:00Z"  # TODO: Use actual timestamp
    }


def format_error(error: str, error_code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
    """Format an error response."""
    return {
        "success": False,
        "error": {
            "message": error,
            "code": error_code
        },
        "timestamp": "2024-01-01T00:00:00Z"  # TODO: Use actual timestamp
    }


def format_conversion_result(content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Format a conversion result."""
    return {
        "content": content,
        "metadata": metadata,
        "format": "markdown"
    }

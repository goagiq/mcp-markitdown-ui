Tool Card: convert_file

General Info

    Name: convert_file
    Title: File Format Converter
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Converts a single file from various formats to Markdown or other supported formats.

Required Libraries

    # Core Python Libraries
    json
    logging
    typing (Dict, List, Any, Optional)
    pathlib

    # MCP and Integration Libraries
    mcp>=1.0.0
    fastapi-mcp>=0.4.0

    # MarkItDown Core
    markitdown[all]>=0.1.3

    # Additional Dependencies
    fastapi>=0.104.0
    pydantic>=2.5.0
    aiofiles>=23.0.0
    python-magic>=0.4.27

Imports and Decorators

    import json
    import logging
    from typing import Dict, Any, Optional
    from pathlib import Path

    logger = logging.getLogger(__name__)

    # MCP Tool Decorator
    # @tool("convert_file")

Intended Use

    For converting individual files from various formats (PDF, DOCX, HTML, etc.) to Markdown.
    Supports both local file paths and remote URLs.
    Returns converted content and metadata.

Out-of-Scope / Limitations

    File size limited by system memory.
    Some formats may require additional system dependencies.
    Remote URLs must be publicly accessible.
    Conversion quality depends on source format complexity.

Input Schema

{
  "type": "object",
  "properties": {
    "file_path": { 
      "type": "string", 
      "description": "Path to input file (local or URL)" 
    },
    "output_format": { 
      "type": "string", 
      "enum": ["markdown", "html", "txt", "pdf"], 
      "default": "markdown",
      "description": "Target output format"
    },
    "options": { 
      "type": "object", 
      "description": "Conversion options",
      "properties": {
        "preserve_formatting": { "type": "boolean", "default": true },
        "include_images": { "type": "boolean", "default": true },
        "extract_tables": { "type": "boolean", "default": true }
      }
    }
  },
  "required": ["file_path"]
}

Output Schema

{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "file_path": { "type": "string" },
    "output_format": { "type": "string" },
    "output_path": { "type": "string" },
    "content": { "type": "string" },
    "metadata": {
      "type": "object",
      "properties": {
        "original_size": { "type": "number" },
        "converted_size": { "type": "number" },
        "processing_time": { "type": "number" },
        "pages": { "type": "number" },
        "word_count": { "type": "number" }
      }
    },
    "error": { "type": "string" }
  },
  "required": ["success", "file_path", "output_format"]
}

Example

    Input:
    { 
      "file_path": "/path/to/document.pdf", 
      "output_format": "markdown",
      "options": {
        "preserve_formatting": true,
        "include_images": true
      }
    }
    Output:
    {
      "success": true,
      "file_path": "/path/to/document.pdf",
      "output_format": "markdown",
      "output_path": "/path/to/document.md",
      "content": "# Document Title\n\nThis is the converted content...",
      "metadata": {
        "original_size": 1024000,
        "converted_size": 51200,
        "processing_time": 2.5,
        "pages": 5,
        "word_count": 1250
      }
    }

Safety & Reliability

    Validates file existence and accessibility.
    Sanitizes file paths to prevent directory traversal.
    Handles various file format edge cases.
    Provides detailed error messages for debugging.
    Logs conversion attempts for monitoring.

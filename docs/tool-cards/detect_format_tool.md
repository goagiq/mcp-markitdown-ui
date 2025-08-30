Tool Card: detect_format

General Info

    Name: detect_format
    Title: File Format Detector
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Detects the format and type of a file using multiple detection methods including file extension, magic bytes, and content analysis.

Required Libraries

    # Core Python Libraries
    json
    logging
    typing (Dict, List, Any, Optional)
    pathlib
    mimetypes

    # MCP and Integration Libraries
    mcp>=1.0.0
    fastapi-mcp>=0.4.0

    # MarkItDown Core
    markitdown[all]>=0.1.3

    # Additional Dependencies
    fastapi>=0.104.0
    pydantic>=2.5.0
    python-magic>=0.4.27
    aiofiles>=23.0.0

Imports and Decorators

    import json
    import logging
    import mimetypes
    from typing import Dict, Any, Optional
    from pathlib import Path
    import magic

    logger = logging.getLogger(__name__)

    # MCP Tool Decorator
    # @tool("detect_format")

Intended Use

    For identifying file formats before conversion processing.
    Supports both local files and remote URLs.
    Provides confidence scores and detailed format information.
    Used for format validation and conversion planning.

Out-of-Scope / Limitations

    Requires file to be accessible (local or remote).
    Some formats may be ambiguous and require additional analysis.
    Remote URLs must be publicly accessible.
    Large files may take longer to analyze.

Input Schema

{
  "type": "object",
  "properties": {
    "file_path": { 
      "type": "string", 
      "description": "Path to file to analyze (local or URL)" 
    },
    "analysis_depth": { 
      "type": "string", 
      "enum": ["basic", "detailed", "full"], 
      "default": "detailed",
      "description": "Level of format analysis to perform"
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
    "detected_format": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "mime_type": { "type": "string" },
    "metadata": {
      "type": "object",
      "properties": {
        "extension": { "type": "string" },
        "file_size": { "type": "number" },
        "detection_method": { "type": "string" },
        "alternative_formats": { 
          "type": "array", 
          "items": { "type": "string" } 
        },
        "is_supported": { "type": "boolean" },
        "converter_available": { "type": "boolean" }
      }
    },
    "error": { "type": "string" }
  },
  "required": ["success", "file_path", "detected_format", "confidence"]
}

Example

    Input:
    { 
      "file_path": "/path/to/document.pdf", 
      "analysis_depth": "detailed"
    }
    Output:
    {
      "success": true,
      "file_path": "/path/to/document.pdf",
      "detected_format": "PDF Document",
      "confidence": 0.95,
      "mime_type": "application/pdf",
      "metadata": {
        "extension": ".pdf",
        "file_size": 1024000,
        "detection_method": "magic_bytes",
        "alternative_formats": ["PDF/A", "PDF/X"],
        "is_supported": true,
        "converter_available": true
      }
    }

Safety & Reliability

    Validates file existence and accessibility.
    Uses multiple detection methods for accuracy.
    Handles corrupted or incomplete files gracefully.
    Provides confidence scores for detection reliability.
    Logs format detection attempts for monitoring.
    Sanitizes file paths to prevent security issues.

Tool Card: list_supported_formats

General Info

    Name: list_supported_formats
    Title: Supported Formats Lister
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Lists all supported input and output file formats with detailed information about converters and capabilities.

Required Libraries

    # Core Python Libraries
    json
    logging
    typing (Dict, List, Any, Optional)

    # MCP and Integration Libraries
    mcp>=1.0.0
    fastapi-mcp>=0.4.0

    # MarkItDown Core
    markitdown[all]>=0.1.3

    # Additional Dependencies
    fastapi>=0.104.0
    pydantic>=2.5.0

Imports and Decorators

    import json
    import logging
    from typing import Dict, List, Any, Optional

    logger = logging.getLogger(__name__)

    # MCP Tool Decorator
    # @tool("list_supported_formats")

Intended Use

    For discovering available file formats and their conversion capabilities.
    Provides information about input formats, output formats, and converters.
    Used for format validation and conversion planning.
    Helps users understand system capabilities.

Out-of-Scope / Limitations

    Only lists currently available formats and converters.
    Does not provide real-time format detection.
    Format availability may depend on system dependencies.
    Some formats may require additional plugins.

Input Schema

{
  "type": "object",
  "properties": {
    "format_type": { 
      "type": "string", 
      "enum": ["input", "output", "all"], 
      "default": "all",
      "description": "Type of formats to list"
    },
    "include_details": { 
      "type": "boolean", 
      "default": true,
      "description": "Include detailed format information"
    }
  }
}

Output Schema

{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "formats": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "extension": { "type": "string" },
          "name": { "type": "string" },
          "description": { "type": "string" },
          "mime_type": { "type": "string" },
          "converter": { "type": "string" },
          "supported": { "type": "boolean" },
          "capabilities": {
            "type": "object",
            "properties": {
              "preserve_formatting": { "type": "boolean" },
              "extract_images": { "type": "boolean" },
              "extract_tables": { "type": "boolean" },
              "extract_links": { "type": "boolean" },
              "metadata_support": { "type": "boolean" }
            }
          },
          "dependencies": { 
            "type": "array", 
            "items": { "type": "string" } 
          }
        }
      }
    },
    "total_formats": { "type": "number" },
    "input_formats": { "type": "number" },
    "output_formats": { "type": "number" },
    "metadata": {
      "type": "object",
      "properties": {
        "last_updated": { "type": "string" },
        "version": { "type": "string" },
        "plugins_loaded": { "type": "number" }
      }
    }
  },
  "required": ["success", "formats", "total_formats"]
}

Example

    Input:
    { 
      "format_type": "all", 
      "include_details": true
    }
    Output:
    {
      "success": true,
      "formats": [
        {
          "extension": ".pdf",
          "name": "PDF Document",
          "description": "Portable Document Format",
          "mime_type": "application/pdf",
          "converter": "pdf_converter",
          "supported": true,
          "capabilities": {
            "preserve_formatting": true,
            "extract_images": true,
            "extract_tables": true,
            "extract_links": true,
            "metadata_support": true
          },
          "dependencies": ["pdfplumber", "PyPDF2"]
        },
        {
          "extension": ".docx",
          "name": "Word Document",
          "description": "Microsoft Word Document",
          "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "converter": "docx_converter",
          "supported": true,
          "capabilities": {
            "preserve_formatting": true,
            "extract_images": true,
            "extract_tables": true,
            "extract_links": true,
            "metadata_support": true
          },
          "dependencies": ["python-docx"]
        },
        {
          "extension": ".md",
          "name": "Markdown",
          "description": "Markdown Text Format",
          "mime_type": "text/markdown",
          "converter": "markdown_converter",
          "supported": true,
          "capabilities": {
            "preserve_formatting": true,
            "extract_images": false,
            "extract_tables": true,
            "extract_links": true,
            "metadata_support": true
          },
          "dependencies": []
        }
      ],
      "total_formats": 15,
      "input_formats": 12,
      "output_formats": 4,
      "metadata": {
        "last_updated": "2024-01-15T10:30:00Z",
        "version": "1.0.0",
        "plugins_loaded": 3
      }
    }

Safety & Reliability

    Provides accurate format information based on available converters.
    Validates format capabilities against actual implementation.
    Handles missing or unavailable converters gracefully.
    Logs format listing requests for monitoring.
    Returns consistent format information across requests.

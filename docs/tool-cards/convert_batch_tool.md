Tool Card: convert_batch

General Info

    Name: convert_batch
    Title: Batch File Format Converter
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Converts multiple files from various formats to Markdown or other supported formats in a single operation.

Required Libraries

    # Core Python Libraries
    json
    logging
    typing (Dict, List, Any, Optional)
    pathlib
    asyncio

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
    import asyncio
    from typing import Dict, List, Any, Optional
    from pathlib import Path

    logger = logging.getLogger(__name__)

    # MCP Tool Decorator
    # @tool("convert_batch")

Intended Use

    For converting multiple files simultaneously from various formats to Markdown.
    Supports both local file paths and remote URLs.
    Returns batch conversion results with individual file status.

Out-of-Scope / Limitations

    Total batch size limited by system memory.
    Processing time scales with number of files.
    Some formats may require additional system dependencies.
    Remote URLs must be publicly accessible.
    Individual file failures don't stop the entire batch.

Input Schema

{
  "type": "object",
  "properties": {
    "file_paths": { 
      "type": "array", 
      "items": { "type": "string" },
      "description": "List of file paths to convert (local or URLs)" 
    },
    "output_format": { 
      "type": "string", 
      "enum": ["markdown", "html", "txt", "pdf"], 
      "default": "markdown",
      "description": "Target output format for all files"
    },
    "options": { 
      "type": "object", 
      "description": "Batch conversion options",
      "properties": {
        "preserve_formatting": { "type": "boolean", "default": true },
        "include_images": { "type": "boolean", "default": true },
        "extract_tables": { "type": "boolean", "default": true },
        "parallel_processing": { "type": "boolean", "default": true },
        "max_concurrent": { "type": "number", "default": 5 }
      }
    }
  },
  "required": ["file_paths"]
}

Output Schema

{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file_path": { "type": "string" },
          "success": { "type": "boolean" },
          "output_path": { "type": "string" },
          "content": { "type": "string" },
          "error": { "type": "string" },
          "metadata": {
            "type": "object",
            "properties": {
              "original_size": { "type": "number" },
              "converted_size": { "type": "number" },
              "processing_time": { "type": "number" }
            }
          }
        }
      }
    },
    "total_files": { "type": "number" },
    "successful_conversions": { "type": "number" },
    "failed_conversions": { "type": "number" },
    "total_processing_time": { "type": "number" }
  },
  "required": ["success", "results", "total_files", "successful_conversions", "failed_conversions"]
}

Example

    Input:
    { 
      "file_paths": [
        "/path/to/document1.pdf",
        "/path/to/document2.docx",
        "/path/to/document3.html"
      ], 
      "output_format": "markdown",
      "options": {
        "preserve_formatting": true,
        "parallel_processing": true,
        "max_concurrent": 3
      }
    }
    Output:
    {
      "success": true,
      "results": [
        {
          "file_path": "/path/to/document1.pdf",
          "success": true,
          "output_path": "/path/to/document1.md",
          "content": "# Document 1\n\nConverted content...",
          "metadata": {
            "original_size": 1024000,
            "converted_size": 51200,
            "processing_time": 2.5
          }
        },
        {
          "file_path": "/path/to/document2.docx",
          "success": true,
          "output_path": "/path/to/document2.md",
          "content": "# Document 2\n\nConverted content...",
          "metadata": {
            "original_size": 2048000,
            "converted_size": 76800,
            "processing_time": 3.2
          }
        },
        {
          "file_path": "/path/to/document3.html",
          "success": false,
          "error": "File not found",
          "metadata": {
            "processing_time": 0.1
          }
        }
      ],
      "total_files": 3,
      "successful_conversions": 2,
      "failed_conversions": 1,
      "total_processing_time": 5.8
    }

Safety & Reliability

    Validates all file paths before processing.
    Implements parallel processing with configurable limits.
    Continues processing even if individual files fail.
    Provides detailed error messages for each failed file.
    Logs batch processing attempts for monitoring.
    Prevents memory exhaustion with large batches.

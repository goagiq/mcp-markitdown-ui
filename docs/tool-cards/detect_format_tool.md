Tool Card: detect_format

General Info

    Name: detect_format
    Title: Document Format Detector
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Detects the format of a document based on file extension or uploaded file.

Required Libraries

    # Core Python Libraries
    json
    logging
    typing (Dict, List, Any, Optional)
    os
    pathlib

    # HTTP and API Libraries
    fastapi>=0.104.0
    pydantic>=2.5.0
    python-multipart>=0.0.6

    # MCP and FastAPI Integration
    fastapi-mcp>=1.0.0
    uvicorn[standard]>=0.24.0

Imports and Decorators

    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from pydantic import BaseModel
    from typing import Optional
    import logging
    import os
    from pathlib import Path

    logger = logging.getLogger(__name__)

    # FastAPI MCP Decorator
    @app.post("/detect_format", operation_id="detect_format")

Intended Use

    For AI assistants and MCP clients to identify document formats before conversion.
    Supports file upload or file path input methods.
    Provides format validation and compatibility checking.

Out-of-Scope / Limitations

    Only detects format by file extension, not content analysis.
    Requires file upload or valid file path.
    Does not validate file content integrity.
    Limited to predefined format mappings.

Input Schema

{
  "type": "object",
  "properties": {
    "file": {
      "type": "object",
      "description": "Uploaded file (multipart/form-data)"
    },
    "file_path": {
      "type": "string",
      "description": "Path to the document file"
    }
  },
  "anyOf": [
    {"required": ["file"]},
    {"required": ["file_path"]}
  ]
}

Output Schema

{
  "type": "object",
  "properties": {
    "format": {
      "type": "string",
      "description": "Detected document format"
    },
    "error": {
      "type": "string",
      "description": "Error message if detection failed"
    }
  },
  "required": ["format"]
}

Example

    Input (file_path):
    { "file_path": "/path/to/document.pdf" }
    
    Output:
    {
      "format": "PDF"
    }

    Input (file upload):
    { "file": "uploaded_file.docx" }
    
    Output:
    {
      "format": "DOCX"
    }

Safety & Reliability

    Validates file existence before detection.
    Handles unknown extensions gracefully.
    Returns consistent format names.
    No file content processing required.
    Safe for various file types.

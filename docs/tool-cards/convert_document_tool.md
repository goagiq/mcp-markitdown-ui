Tool Card: convert_document

General Info

    Name: convert_document
    Title: Document to Markdown Converter
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Converts various document formats (PDF, DOCX, PPTX, etc.) to markdown format using advanced OCR and text extraction capabilities.

Required Libraries

    # Core Python Libraries
    json
    logging
    typing (Dict, List, Any, Optional)
    os
    tempfile
    base64
    pathlib

    # HTTP and API Libraries
    fastapi>=0.104.0
    pydantic>=2.5.0
    python-multipart>=0.0.6

    # MCP and FastAPI Integration
    fastapi-mcp>=1.0.0
    uvicorn[standard]>=0.24.0

    # MarkItDown Core
    markitdown (local package)

Imports and Decorators

    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from pydantic import BaseModel
    from typing import Optional
    import logging
    import os
    import tempfile
    from pathlib import Path
    import base64

    logger = logging.getLogger(__name__)

    # FastAPI MCP Decorator
    @app.post("/convert", operation_id="convert_document")

Intended Use

    For AI assistants and MCP clients needing to convert documents to markdown format.
    Supports multiple input methods: file upload, file path, or base64 content.
    Handles various document formats with OCR capabilities for scanned documents.

Out-of-Scope / Limitations

    Requires valid file format (PDF, DOCX, PPTX, etc.).
    Large files may take time to process.
    OCR quality depends on document scan quality.
    Temporary files are created and cleaned up automatically.

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
      "description": "Path to the document file to convert"
    },
    "file_content": {
      "type": "string",
      "description": "Base64 encoded file content"
    },
    "file_name": {
      "type": "string",
      "description": "Name of the file (required if using file_content)"
    }
  },
  "anyOf": [
    {"required": ["file"]},
    {"required": ["file_path"]},
    {"required": ["file_content", "file_name"]}
  ]
}

Output Schema

{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the conversion was successful"
    },
    "markdown": {
      "type": "string",
      "description": "The converted markdown content"
    },
    "text_length": {
      "type": "integer",
      "description": "Length of the converted text"
    },
    "error": {
      "type": "string",
      "description": "Error message if conversion failed"
    }
  },
  "required": ["success", "markdown", "text_length"]
}

Example

    Input (file_path):
    { "file_path": "/path/to/document.pdf" }
    
    Output:
    {
      "success": true,
      "markdown": "# Document Title\n\nThis is the converted content...",
      "text_length": 1250
    }

    Input (file_content):
    { 
      "file_content": "base64_encoded_content_here",
      "file_name": "document.docx"
    }

Safety & Reliability

    Validates file existence and format before processing.
    Handles temporary file cleanup automatically.
    Returns detailed error messages for debugging.
    Supports multiple input methods for flexibility.
    Uses secure file handling practices.

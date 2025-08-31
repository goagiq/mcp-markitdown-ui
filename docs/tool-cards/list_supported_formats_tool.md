Tool Card: list_supported_formats

General Info

    Name: list_supported_formats
    Title: Supported Formats Lister
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Lists all document formats supported by the MarkItDown conversion system.

Required Libraries

    # Core Python Libraries
    json
    logging
    typing (Dict, List, Any, Optional)

    # HTTP and API Libraries
    fastapi>=0.104.0
    pydantic>=2.5.0

    # MCP and FastAPI Integration
    fastapi-mcp>=1.0.0
    uvicorn[standard]>=0.24.0

Imports and Decorators

    from fastapi import FastAPI
    from pydantic import BaseModel
    import logging

    logger = logging.getLogger(__name__)

    # FastAPI MCP Decorator
    @app.get("/supported_formats", operation_id="list_supported_formats")

Intended Use

    For AI assistants and MCP clients to discover available document formats.
    Provides a comprehensive list of supported file types for conversion.
    Useful for validation and user guidance before attempting conversion.

Out-of-Scope / Limitations

    Read-only operation; no file processing.
    Returns static list of supported formats.
    Does not validate individual file compatibility.

Input Schema

{
  "type": "object",
  "properties": {},
  "additionalProperties": false
}

Output Schema

{
  "type": "object",
  "properties": {
    "formats": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of supported document formats"
    }
  },
  "required": ["formats"]
}

Example

    Input:
    {}
    
    Output:
    {
      "formats": [
        "PDF", "DOCX", "DOC", "PPTX", "PPT", "XLSX", "XLS",
        "TXT", "MD", "HTML", "HTM", "EPUB", "CSV", "ZIP"
      ]
    }

Safety & Reliability

    No file system access required.
    Returns consistent, predefined list.
    No external dependencies or API calls.
    Fast and reliable response.

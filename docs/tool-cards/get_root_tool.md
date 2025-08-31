Tool Card: get_root

General Info

    Name: get_root
    Title: MCP Server Root Endpoint
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Provides basic information about the MarkItDown MCP server and available endpoints.

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
    import logging

    logger = logging.getLogger(__name__)

    # FastAPI MCP Decorator
    @app.get("/", operation_id="get_root")

Intended Use

    For AI assistants and MCP clients to discover server capabilities.
    Provides service information and endpoint documentation.
    Used for health checks and server discovery.

Out-of-Scope / Limitations

    Read-only operation; no data processing.
    Returns static server information.
    No authentication or authorization required.

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
    "service": {
      "type": "string",
      "description": "Service name"
    },
    "version": {
      "type": "string",
      "description": "Service version"
    },
    "endpoints": {
      "type": "object",
      "properties": {
        "convert": {
          "type": "string",
          "description": "Document conversion endpoint"
        },
        "detect_format": {
          "type": "string",
          "description": "Format detection endpoint"
        },
        "supported_formats": {
          "type": "string",
          "description": "Supported formats endpoint"
        },
        "health": {
          "type": "string",
          "description": "Health check endpoint"
        }
      }
    }
  },
  "required": ["service", "version", "endpoints"]
}

Example

    Input:
    {}
    
    Output:
    {
      "service": "MarkItDown MCP Server",
      "version": "1.0.0",
      "endpoints": {
        "convert": "/convert",
        "detect_format": "/detect_format",
        "supported_formats": "/supported_formats",
        "health": "/health"
      }
    }

Safety & Reliability

    No external dependencies or API calls.
    Returns consistent server information.
    Fast and reliable response.
    No file system access required.

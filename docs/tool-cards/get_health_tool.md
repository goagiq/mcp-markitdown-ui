Tool Card: get_health

General Info

    Name: get_health
    Title: MCP Server Health Check
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Provides health status information for the MarkItDown MCP server.

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
    @app.get("/health", operation_id="get_health")

Intended Use

    For AI assistants and MCP clients to check server health status.
    Provides basic health monitoring and status reporting.
    Used for service availability checks and monitoring.

Out-of-Scope / Limitations

    Read-only operation; no data processing.
    Returns basic health status only.
    No detailed system diagnostics.

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
    "status": {
      "type": "string",
      "description": "Health status (healthy/unhealthy)"
    },
    "service": {
      "type": "string",
      "description": "Service identifier"
    },
    "version": {
      "type": "string",
      "description": "Service version"
    }
  },
  "required": ["status", "service", "version"]
}

Example

    Input:
    {}
    
    Output:
    {
      "status": "healthy",
      "service": "markitdown-mcp",
      "version": "1.0.0"
    }

Safety & Reliability

    No external dependencies or API calls.
    Returns consistent health status.
    Fast and reliable response.
    No file system access required.

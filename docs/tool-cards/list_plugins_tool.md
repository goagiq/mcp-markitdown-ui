Tool Card: list_plugins

General Info

    Name: list_plugins
    Title: Plugin Manager
    Version: 1.0.0
    Author: MarkItDown Team
    Description: Lists all available MarkItDown plugins with their capabilities, supported formats, and status information.

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
    # @tool("list_plugins")

Intended Use

    For discovering available plugins and their capabilities.
    Provides information about plugin status, supported formats, and dependencies.
    Used for plugin management and system configuration.
    Helps users understand available conversion options.

Out-of-Scope / Limitations

    Only lists currently loaded plugins.
    Does not install or manage plugins.
    Plugin availability may depend on system configuration.
    Some plugins may require additional system dependencies.

Input Schema

{
  "type": "object",
  "properties": {
    "plugin_type": { 
      "type": "string", 
      "enum": ["converter", "formatter", "all"], 
      "default": "all",
      "description": "Type of plugins to list"
    },
    "include_details": { 
      "type": "boolean", 
      "default": true,
      "description": "Include detailed plugin information"
    },
    "status_filter": { 
      "type": "string", 
      "enum": ["active", "inactive", "all"], 
      "default": "all",
      "description": "Filter plugins by status"
    }
  }
}

Output Schema

{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "plugins": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "version": { "type": "string" },
          "description": { "type": "string" },
          "type": { "type": "string" },
          "status": { "type": "string" },
          "supported_formats": { 
            "type": "array", 
            "items": { "type": "string" } 
          },
          "capabilities": {
            "type": "object",
            "properties": {
              "conversion": { "type": "boolean" },
              "formatting": { "type": "boolean" },
              "validation": { "type": "boolean" },
              "metadata_extraction": { "type": "boolean" }
            }
          },
          "dependencies": { 
            "type": "array", 
            "items": { "type": "string" } 
          },
          "author": { "type": "string" },
          "license": { "type": "string" },
          "last_updated": { "type": "string" }
        }
      }
    },
    "total_plugins": { "type": "number" },
    "active_plugins": { "type": "number" },
    "inactive_plugins": { "type": "number" },
    "metadata": {
      "type": "object",
      "properties": {
        "plugin_directory": { "type": "string" },
        "auto_load_enabled": { "type": "boolean" },
        "last_scan": { "type": "string" }
      }
    }
  },
  "required": ["success", "plugins", "total_plugins"]
}

Example

    Input:
    { 
      "plugin_type": "all", 
      "include_details": true,
      "status_filter": "all"
    }
    Output:
    {
      "success": true,
      "plugins": [
        {
          "name": "pdf_converter",
          "version": "1.2.0",
          "description": "Converts PDF documents to Markdown with formatting preservation",
          "type": "converter",
          "status": "active",
          "supported_formats": [".pdf", ".PDF"],
          "capabilities": {
            "conversion": true,
            "formatting": true,
            "validation": true,
            "metadata_extraction": true
          },
          "dependencies": ["pdfplumber", "PyPDF2"],
          "author": "MarkItDown Team",
          "license": "MIT",
          "last_updated": "2024-01-10T15:30:00Z"
        },
        {
          "name": "docx_converter",
          "version": "1.1.5",
          "description": "Converts Microsoft Word documents to Markdown",
          "type": "converter",
          "status": "active",
          "supported_formats": [".docx", ".doc"],
          "capabilities": {
            "conversion": true,
            "formatting": true,
            "validation": true,
            "metadata_extraction": true
          },
          "dependencies": ["python-docx"],
          "author": "MarkItDown Team",
          "license": "MIT",
          "last_updated": "2024-01-08T12:15:00Z"
        },
        {
          "name": "html_formatter",
          "version": "1.0.2",
          "description": "Formats HTML content for better Markdown conversion",
          "type": "formatter",
          "status": "active",
          "supported_formats": [".html", ".htm"],
          "capabilities": {
            "conversion": false,
            "formatting": true,
            "validation": true,
            "metadata_extraction": false
          },
          "dependencies": ["beautifulsoup4"],
          "author": "MarkItDown Team",
          "license": "MIT",
          "last_updated": "2024-01-05T09:45:00Z"
        }
      ],
      "total_plugins": 3,
      "active_plugins": 3,
      "inactive_plugins": 0,
      "metadata": {
        "plugin_directory": "/plugins",
        "auto_load_enabled": true,
        "last_scan": "2024-01-15T10:30:00Z"
      }
    }

Safety & Reliability

    Provides accurate plugin information based on loaded plugins.
    Validates plugin status and capabilities.
    Handles missing or corrupted plugins gracefully.
    Logs plugin listing requests for monitoring.
    Returns consistent plugin information across requests.
    Validates plugin dependencies and requirements.

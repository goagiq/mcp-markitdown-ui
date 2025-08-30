"""Information tools for MarkItDown MCP server."""

from typing import Any, Dict

from markitdown import MarkItDown

from .base import BaseTool


class ListSupportedFormatsTool(BaseTool):
    """Tool for listing supported file formats."""

    def _get_description(self) -> str:
        return "List all supported file formats"

    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the format listing."""
        self._validate_arguments(arguments)
        self._log_execution(arguments)

        try:
            # Initialize MarkItDown
            markitdown = MarkItDown()

            # Get supported formats
            supported_formats = markitdown._get_supported_formats()

            # Format the response
            formats = []
            for format_name, format_info in supported_formats.items():
                formats.append({
                    "format": format_name,
                    "description": format_info.get("description", ""),
                    "extensions": format_info.get("extensions", []),
                    "mime_types": format_info.get("mime_types", [])
                })

            response = {
                "formats": formats,
                "total_formats": len(formats)
            }

            self._log_result(response)
            return response

        except Exception as e:
            response = {
                "formats": [],
                "total_formats": 0,
                "error": str(e)
            }

            self._log_result(response)
            return response


class ListPluginsTool(BaseTool):
    """Tool for listing available plugins."""

    def _get_description(self) -> str:
        return "List all available plugins"

    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin listing."""
        self._validate_arguments(arguments)
        self._log_execution(arguments)

        try:
            # Initialize MarkItDown
            markitdown = MarkItDown()

            # Get available plugins
            plugins = markitdown._get_available_plugins()

            # Format the response
            plugin_list = []
            for plugin_name, plugin_info in plugins.items():
                plugin_list.append({
                    "name": plugin_name,
                    "description": plugin_info.get("description", ""),
                    "version": plugin_info.get("version", "unknown"),
                    "enabled": plugin_info.get("enabled", False)
                })

            response = {
                "plugins": plugin_list,
                "total_plugins": len(plugin_list)
            }

            self._log_result(response)
            return response

        except Exception as e:
            response = {
                "plugins": [],
                "total_plugins": 0,
                "error": str(e)
            }

            self._log_result(response)
            return response

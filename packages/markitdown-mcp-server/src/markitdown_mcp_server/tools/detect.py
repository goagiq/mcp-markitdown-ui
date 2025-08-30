"""Format detection tool for MarkItDown MCP server."""

import mimetypes
from typing import Any, Dict

from markitdown import MarkItDown

from .base import BaseTool


class DetectFormatTool(BaseTool):
    """Tool for detecting file formats."""

    def _get_description(self) -> str:
        return "Detect the format of a file"

    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "file_url": {
                    "type": "string",
                    "description": "URL of the file"
                }
            },
            "required": ["file_path"] or ["file_url"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the format detection."""
        self._validate_arguments(arguments)
        self._log_execution(arguments)

        try:
            # Get file path or URL
            file_path = arguments.get("file_path")
            file_url = arguments.get("file_url")

            if not file_path and not file_url:
                raise ValueError("Either file_path or file_url must be provided")

            # Initialize MarkItDown
            markitdown = MarkItDown()

            # Detect format
            if file_path:
                stream_info = markitdown._get_stream_info(file_path)
            else:
                stream_info = markitdown._get_stream_info(file_url)

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path or file_url)

            # Check if format is supported
            supported = markitdown._is_format_supported(stream_info)

            response = {
                "format": stream_info.format,
                "mime_type": mime_type or "unknown",
                "confidence": 0.9,  # High confidence for detected formats
                "supported": supported,
                "metadata": {
                    "file_size": getattr(stream_info, 'file_size', 0),
                    "encoding": getattr(stream_info, 'encoding', 'unknown')
                }
            }

            self._log_result(response)
            return response

        except Exception as e:
            response = {
                "format": "unknown",
                "mime_type": "unknown",
                "confidence": 0.0,
                "supported": False,
                "error": str(e),
                "metadata": {}
            }

            self._log_result(response)
            return response

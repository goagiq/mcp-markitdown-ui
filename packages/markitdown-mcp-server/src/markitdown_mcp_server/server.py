"""MarkItDown MCP Server implementation."""

import json
import logging
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
)

from .tools.convert import ConvertFileTool, ConvertBatchTool
from .tools.detect import DetectFormatTool
from .tools.info import ListSupportedFormatsTool, ListPluginsTool

logger = logging.getLogger(__name__)


class MarkItDownMCPServer:
    """MCP Server for MarkItDown file conversion tools."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server = Server("markitdown-mcp")
        self._setup_tools()
        self._setup_handlers()

    def _setup_tools(self) -> None:
        """Set up all available tools."""
        self.tools = {
            "convert_file": ConvertFileTool(),
            "convert_batch": ConvertBatchTool(),
            "detect_format": DetectFormatTool(),
            "list_supported_formats": ListSupportedFormatsTool(),
            "list_plugins": ListPluginsTool(),
        }

    def _setup_handlers(self) -> None:
        """Set up server event handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """Handle list tools request."""
            tools = []
            for tool_id, tool in self.tools.items():
                tools.append(
                    Tool(
                        name=tool_id,
                        description=tool.description,
                        inputSchema=tool.input_schema,
                    )
                )
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool call request."""
            try:
                if name not in self.tools:
                    raise ValueError(f"Unknown tool: {name}")
                
                tool = self.tools[name]
                result = await tool.execute(arguments)
                
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                )
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": json.dumps({"error": str(e)}, indent=2)
                        }
                    ],
                    isError=True
                )

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="markitdown-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

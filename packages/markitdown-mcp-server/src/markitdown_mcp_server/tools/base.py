"""Base tool class for MarkItDown MCP tools."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all MarkItDown MCP tools."""

    def __init__(self) -> None:
        """Initialize the tool."""
        self.name = self.__class__.__name__
        self.description = self._get_description()
        self.input_schema = self._get_input_schema()

    @abstractmethod
    def _get_description(self) -> str:
        """Get the tool description."""
        pass

    @abstractmethod
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for the tool."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given arguments."""
        pass

    def _validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate the input arguments against the schema."""
        # Basic validation - in a real implementation, you'd use a proper JSON schema
        # validator
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")

    def _log_execution(self, arguments: Dict[str, Any]) -> None:
        """Log tool execution for debugging."""
        logger.debug(
            f"Executing {self.name} with arguments: {json.dumps(arguments)}"
        )

    def _log_result(self, result: Dict[str, Any]) -> None:
        """Log tool result for debugging."""
        logger.debug(
            f"{self.name} result: {json.dumps(result)}"
        )

"""
Base converter classes for MarkItDown.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, BinaryIO, Optional

from ._stream_info import StreamInfo


@dataclass
class DocumentConverterResult:
    """Result of a document conversion."""
    
    markdown: str
    metadata: Optional[dict[str, Any]] = None


class DocumentConverter(ABC):
    """Base class for document converters."""
    
    @abstractmethod
    def convert(self, file_path: str, stream_info: Optional[StreamInfo] = None) -> DocumentConverterResult:
        """Convert a file to markdown."""
        pass
    
    @abstractmethod
    def convert_stream(self, stream: BinaryIO, stream_info: Optional[StreamInfo] = None) -> DocumentConverterResult:
        """Convert a stream to markdown."""
        pass


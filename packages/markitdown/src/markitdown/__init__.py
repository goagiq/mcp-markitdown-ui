"""
MarkItDown - A simple text-based document reader for LLM use.
"""

from ._markitdown import MarkItDown
from ._stream_info import StreamInfo
from ._base_converter import DocumentConverter, DocumentConverterResult

__all__ = [
    "MarkItDown",
    "StreamInfo", 
    "DocumentConverter",
    "DocumentConverterResult",
]


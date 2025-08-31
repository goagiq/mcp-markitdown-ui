"""
Stream information for file processing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StreamInfo:
    """Information about a data stream."""
    
    filename: Optional[str] = None
    extension: Optional[str] = None
    mimetype: Optional[str] = None
    charset: Optional[str] = None


"""
Stream information for file processing.
"""

from dataclasses import dataclass, replace
from typing import Optional


@dataclass
class StreamInfo:
    """Information about a data stream."""
    
    filename: Optional[str] = None
    extension: Optional[str] = None
    mimetype: Optional[str] = None
    charset: Optional[str] = None
    local_path: Optional[str] = None
    url: Optional[str] = None
    
    def copy_and_update(self, **kwargs):
        """Create a copy of this StreamInfo with updated fields."""
        return replace(self, **kwargs)


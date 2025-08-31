"""
Plain text converter for MarkItDown
"""

import os
import logging
from typing import Optional, BinaryIO, Any

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

logger = logging.getLogger(__name__)


class PlainTextConverter(DocumentConverter):
    """Convert plain text files to markdown."""
    
    def __init__(self):
        pass
    
    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """Check if this converter can handle the given file."""
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ['.txt', '.md']:
            return True
        if mimetype.startswith('text/'):
            return True
        return False
    
    def convert(self, file_path_or_stream, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert plain text file to markdown."""
        try:
            # Handle both file path and stream
            if isinstance(file_path_or_stream, str):
                file_path = file_path_or_stream
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
            else:
                # It's a stream, use convert_stream
                return self.convert_stream(file_path_or_stream, stream_info, **kwargs)
            
            # Read the text file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    raise ValueError(f"Could not read file {file_path}: {e}")
            
            # For .md files, return as-is
            if file_path.lower().endswith('.md'):
                markdown_content = content
            else:
                # For .txt files, convert to markdown
                # Split into lines and add markdown formatting
                lines = content.split('\n')
                markdown_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        markdown_lines.append('')
                    elif line.startswith('#'):
                        # Already looks like markdown
                        markdown_lines.append(line)
                    elif line.isupper() and len(line) > 3:
                        # All caps line might be a heading
                        markdown_lines.append(f'## {line}')
                    elif line.startswith('- ') or line.startswith('* '):
                        # Already looks like a list
                        markdown_lines.append(line)
                    elif line.startswith('1. '):
                        # Numbered list
                        markdown_lines.append(line)
                    else:
                        # Regular text
                        markdown_lines.append(line)
                
                markdown_content = '\n'.join(markdown_lines)
            
            return DocumentConverterResult(markdown=markdown_content)
            
        except Exception as e:
            logger.error(f"Error in plain text conversion: {e}")
            raise
    
    def convert_stream(self, stream: BinaryIO, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert stream to markdown"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(stream.read())
            temp_path = temp_file.name
        
        try:
            return self.convert(temp_path, stream_info)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

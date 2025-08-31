"""
ZIP converter for MarkItDown
"""

import os
import zipfile
import tempfile
import logging
from typing import Optional, List, BinaryIO, Any

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

logger = logging.getLogger(__name__)


class ZipConverter(DocumentConverter):
    """Convert ZIP files to markdown by extracting and processing contents."""
    
    def __init__(self, markitdown=None):
        self.markitdown = markitdown
    
    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """Check if this converter can handle the given file."""
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension == '.zip':
            return True
        if mimetype == 'application/zip':
            return True
        return False
    
    def convert(self, file_path_or_stream, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert ZIP file to markdown by extracting and processing contents."""
        try:
            # Handle both file path and stream
            if isinstance(file_path_or_stream, str):
                file_path = file_path_or_stream
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
            else:
                # It's a stream, use convert_stream
                return self.convert_stream(file_path_or_stream, stream_info, **kwargs)
            
            if not zipfile.is_zipfile(file_path):
                raise ValueError(f"File is not a valid ZIP file: {file_path}")
            
            markdown_content = f"# ZIP Archive Contents\n\n"
            markdown_content += f"**Archive:** `{os.path.basename(file_path)}`\n\n"
            
            # Extract ZIP contents to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # List all files in the ZIP
                    file_list = zip_ref.namelist()
                    markdown_content += f"**Total Files:** {len(file_list)}\n\n"
                    
                    # Extract all files
                    zip_ref.extractall(temp_dir)
                    
                    # Process each file if markitdown instance is available
                    if self.markitdown:
                        markdown_content += "## Extracted Files\n\n"
                        
                        for file_name in file_list:
                            if not file_name.endswith('/'):  # Skip directories
                                file_path_in_zip = os.path.join(temp_dir, file_name)
                                
                                if os.path.isfile(file_path_in_zip):
                                    try:
                                        # Try to convert the file using markitdown
                                        result = self.markitdown.convert(file_path_in_zip)
                                        markdown_content += f"### {file_name}\n\n"
                                        markdown_content += f"{result.markdown}\n\n"
                                        markdown_content += "---\n\n"
                                    except Exception as e:
                                        logger.warning(f"Could not convert {file_name}: {e}")
                                        # Add file info without conversion
                                        file_size = os.path.getsize(file_path_in_zip)
                                        markdown_content += f"### {file_name}\n\n"
                                        markdown_content += f"*File size: {file_size} bytes*\n\n"
                                        markdown_content += f"*Could not convert: {str(e)}*\n\n"
                                        markdown_content += "---\n\n"
                    else:
                        # Just list files if no markitdown instance
                        markdown_content += "## File List\n\n"
                        for file_name in file_list:
                            if not file_name.endswith('/'):
                                markdown_content += f"- `{file_name}`\n"
            
            return DocumentConverterResult(markdown=markdown_content)
            
        except Exception as e:
            logger.error(f"Error in ZIP conversion: {e}")
            raise
    
    def convert_stream(self, stream: BinaryIO, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert stream to markdown"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_file.write(stream.read())
            temp_path = temp_file.name
        
        try:
            return self.convert(temp_path, stream_info)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

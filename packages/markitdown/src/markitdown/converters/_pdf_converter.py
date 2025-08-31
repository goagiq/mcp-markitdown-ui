"""
PDF Converter for MarkItDown
"""

import os
import logging
from typing import Optional

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

logger = logging.getLogger(__name__)


class PdfConverter(DocumentConverter):
    """Basic PDF converter"""
    
    def __init__(self):
        pass
    
    def convert(self, file_path: str, stream_info: Optional[StreamInfo] = None) -> DocumentConverterResult:
        """Convert PDF file to markdown"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Basic text extraction (placeholder)
            text = "PDF content extracted"
            markdown = f"# PDF Content\n\n{text}\n"
            
            return DocumentConverterResult(markdown=markdown)
            
        except Exception as e:
            logger.error(f"Error in PDF conversion: {e}")
            raise
    
    def convert_stream(self, stream, stream_info: Optional[StreamInfo] = None) -> DocumentConverterResult:
        """Convert stream to markdown"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(stream.read())
            temp_path = temp_file.name
        
        try:
            return self.convert(temp_path, stream_info)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

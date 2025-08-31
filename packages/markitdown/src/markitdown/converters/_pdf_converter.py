"""
PDF Converter for MarkItDown
"""

import os
import logging
from typing import Optional, BinaryIO, Any

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

logger = logging.getLogger(__name__)


class PdfConverter(DocumentConverter):
    """Basic PDF converter"""
    
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

        if extension == '.pdf':
            return True
        if mimetype == 'application/pdf':
            return True
        return False
    
    def convert(self, file_path_or_stream, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert PDF file to markdown"""
        try:
            # Handle both file path and stream
            if isinstance(file_path_or_stream, str):
                file_path = file_path_or_stream
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
            else:
                # It's a stream, use convert_stream
                return self.convert_stream(file_path_or_stream, stream_info, **kwargs)
            
            # Extract text from PDF using PyMuPDF
            text_content = self._extract_text_from_pdf(file_path)
            
            # Get filename for title
            filename = stream_info.filename if stream_info and stream_info.filename else os.path.basename(file_path)
            
            # Create markdown with proper formatting
            markdown = f"# {filename}\n\n{text_content}\n"
            
            return DocumentConverterResult(markdown=markdown)
            
        except Exception as e:
            logger.error(f"Error in PDF conversion: {e}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            all_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    all_text.append(text.strip())
            
            doc.close()
            
            # Join all text with page separators
            if len(all_text) > 1:
                return "\n\n--- Page Break ---\n\n".join(all_text)
            else:
                return "\n\n".join(all_text)
                
        except ImportError:
            logger.error("PyMuPDF not available for PDF text extraction")
            return "PDF text extraction requires PyMuPDF"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return f"Error extracting text: {str(e)}"
    
    def convert_stream(self, stream: BinaryIO, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
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

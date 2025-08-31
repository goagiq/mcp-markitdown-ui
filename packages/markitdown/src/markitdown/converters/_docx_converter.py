import os
import logging
from typing import Optional, BinaryIO, Any
import zipfile
import xml.etree.ElementTree as ET

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

logger = logging.getLogger(__name__)


class DocxConverter(DocumentConverter):
    """Basic Word document converter"""

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

        if extension in ['.docx', '.doc']:
            return True
        if mimetype in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                       'application/msword']:
            return True
        return False

    def convert(self, file_path_or_stream, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert Word document to markdown"""
        try:
            # Handle both file path and stream
            if isinstance(file_path_or_stream, str):
                file_path = file_path_or_stream
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
            else:
                # It's a stream, use convert_stream
                return self.convert_stream(file_path_or_stream, stream_info, **kwargs)

            # Extract text from DOCX file
            text_content = self._extract_text_from_docx(file_path)
            markdown = f"# {os.path.basename(file_path)}\n\n{text_content}\n"

            return DocumentConverterResult(markdown=markdown)

        except Exception as e:
            logger.error(f"Error in DOCX conversion: {e}")
            raise

    def convert_stream(self, stream: BinaryIO, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert stream to markdown"""
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(stream.read())
            temp_path = temp_file.name

        try:
            return self.convert(temp_path, stream_info, **kwargs)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text content from DOCX file"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Read the main document content
                if 'word/document.xml' in zip_file.namelist():
                    xml_content = zip_file.read('word/document.xml')
                    root = ET.fromstring(xml_content)
                    
                    # Extract text from paragraphs
                    text_parts = []
                    for paragraph in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                        para_text = ''
                        for text_elem in paragraph.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                            if text_elem.text:
                                para_text += text_elem.text
                        if para_text.strip():
                            text_parts.append(para_text.strip())
                    
                    return '\n\n'.join(text_parts)
                else:
                    return "Could not extract text from DOCX file"
                    
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return f"Error extracting text: {str(e)}"

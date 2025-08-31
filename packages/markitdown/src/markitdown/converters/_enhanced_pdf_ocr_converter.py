"""
Enhanced PDF OCR Converter for MarkItDown.

This module provides an enhanced PDF converter that intelligently handles
both text-based and image-based PDFs:

1. If PDF is text-based, process normally using traditional text extraction
2. Else, convert each page to PNG using PyMuPDF and use vision OCR
"""

import sys
import logging
import time
from typing import BinaryIO, Any

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo
from .._exceptions import MissingDependencyException
from ._pdf_converter import PdfConverter
from ._vision_ocr_converter import VisionOcrConverter
from ..converter_utils.vision_ocr.pdf_processor import PdfProcessor, PdfType

logger = logging.getLogger(__name__)

# Try loading optional dependencies
_dependency_exc_info = None
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    _dependency_exc_info = sys.exc_info()


ACCEPTED_MIME_TYPE_PREFIXES = [
    "application/pdf",
    "application/x-pdf",
]

ACCEPTED_FILE_EXTENSIONS = [".pdf"]


class EnhancedPdfOcrConverter(DocumentConverter):
    """
    Enhanced PDF OCR Converter that intelligently handles text-based and image-based PDFs.
    
    Logic:
    1. If PDF is text-based, process normally using traditional text extraction
    2. Else, convert each page to PNG using PyMuPDF and use vision OCR
    """
    
    def __init__(
        self,
        vision_model: str = "llava:7b",
        use_hybrid_ocr: bool = True,
        max_image_size: int = 800,
        use_grayscale: bool = True,
        compression_quality: int = 85,
        timeout: int = 300,
        zoom_factor: float = 2.0,
        fallback_to_tesseract: bool = True
    ):
        """
        Initialize the Enhanced PDF OCR Converter.
        
        Args:
            vision_model: Ollama vision model to use for OCR
            use_hybrid_ocr: Whether to use hybrid OCR approach
            max_image_size: Maximum image dimension for processing
            use_grayscale: Whether to convert images to grayscale
            compression_quality: JPEG compression quality (1-100)
            timeout: Processing timeout in seconds
            zoom_factor: Zoom factor for PDF to image conversion
        """
        # Check dependencies
        if not PYMUPDF_AVAILABLE:
            raise MissingDependencyException(
                "PyMuPDF not available. Install with: pip install PyMuPDF"
            ) from _dependency_exc_info[1] if _dependency_exc_info else None
        
        # Initialize converters
        self.pdf_converter = PdfConverter()
        self.vision_ocr_converter = VisionOcrConverter(
            model=vision_model,
            use_hybrid_ocr=use_hybrid_ocr,
            max_image_size=max_image_size,
            use_grayscale=use_grayscale,
            compression_quality=compression_quality,
            timeout=timeout
        )
        
        # Update Ollama client to use host network for local Ollama
        if hasattr(self.vision_ocr_converter, 'ollama_client'):
            self.vision_ocr_converter.ollama_client.host = "http://host.docker.internal:11434"
            # Also update the client's base URL
            if hasattr(self.vision_ocr_converter.ollama_client, 'client'):
                self.vision_ocr_converter.ollama_client.client.base_url = "http://host.docker.internal:11434"
        self.pdf_processor = PdfProcessor(zoom_factor=zoom_factor)
        self.fallback_to_tesseract = fallback_to_tesseract
        
                         # Define fallback vision models to try in order
                 # Prioritize llama3.2-vision as it's more stable
                 self.fallback_vision_models = [
                     "llama3.2-vision:latest",
                     "minicpm-v:latest",
                     "llava:latest",
                     "llava:7b",
                     "llava:13b", 
                     "bakllava:latest",
                     "llava:7b-v1.6",
                     "llava:13b-v1.6"
                 ]
        
        logger.info(f"Initialized Enhanced PDF OCR Converter with vision model: {vision_model}")
    
    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """
        Check if this converter can handle the given file.
        
        Args:
            file_stream: File stream to check
            stream_info: Stream information
            **kwargs: Additional arguments
            
        Returns:
            True if converter can handle the file, False otherwise
        """
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()
        
        # Check file extension
        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True
        
        # Check MIME type
        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True
        
        return False
    
    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """
        Convert PDF to markdown using enhanced logic.
        
        Args:
            file_stream: PDF file stream
            stream_info: Stream information
            **kwargs: Additional arguments
            
        Returns:
            DocumentConverterResult containing extracted text
        """
        start_time = time.time()
        
        try:
            # Read file data
            file_data = file_stream.read()
            file_stream.seek(0)  # Reset stream position
            
            # Analyze PDF type
            pdf_type = self.pdf_processor.analyze_pdf_type(file_data)
            logger.info(f"PDF type detected: {pdf_type.value}")
            
            # Process based on PDF type
            if pdf_type == PdfType.TEXT_BASED:
                logger.info("Processing text-based PDF with traditional extraction")
                result = self._process_text_based_pdf(file_stream, stream_info, **kwargs)
            else:
                logger.info("Processing image-based PDF with Vision OCR")
                result = self._process_image_based_pdf(file_data, stream_info, **kwargs)
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Add processing metadata
            markdown_content = result.markdown
            markdown_content += f"\n\n**Total Processing Time:** {total_time:.2f}s"
            
            return DocumentConverterResult(markdown=markdown_content)
            
        except Exception as e:
            logger.error(f"Enhanced PDF OCR conversion failed: {e}")
            raise MissingDependencyException(
                f"Enhanced PDF OCR conversion failed: {e}"
            ) from e
    
    def _process_text_based_pdf(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any
    ) -> DocumentConverterResult:
        """
        Process text-based PDF using traditional extraction.
        
        Args:
            file_stream: PDF file stream
            stream_info: Stream information
            **kwargs: Additional arguments
            
        Returns:
            DocumentConverterResult containing extracted text
        """
        try:
            # Use traditional PDF converter
            result = self.pdf_converter.convert(file_stream, stream_info, **kwargs)
            
            # Add metadata
            markdown_content = result.markdown
            markdown_content += "\n\n---\n"
            markdown_content += "### Processing Information\n"
            markdown_content += "**Processing Method:** Traditional PDF text extraction\n"
            markdown_content += "**PDF Type:** Text-based\n"
            markdown_content += "**Confidence:** High\n"
            
            return DocumentConverterResult(markdown=markdown_content)
            
        except Exception as e:
            logger.error(f"Text-based PDF processing failed: {e}")
            raise
    
    def _process_image_based_pdf(
        self,
        file_data: bytes,
        stream_info: StreamInfo,
        **kwargs: Any
    ) -> DocumentConverterResult:
        """
        Process image-based PDF using Vision OCR with Tesseract fallback.
        
        Args:
            file_data: PDF file data as bytes
            stream_info: Stream information
            **kwargs: Additional arguments
            
        Returns:
            DocumentConverterResult containing extracted text
        """
        """
        Process image-based PDF using Vision OCR.
        
        Args:
            file_data: PDF file data as bytes
            stream_info: Stream information
            **kwargs: Additional arguments
            
        Returns:
            DocumentConverterResult containing extracted text
        """
        try:
            # Convert PDF to images
            images = self.pdf_processor.pdf_to_images(file_data)
            
            if not images:
                raise Exception("No images extracted from PDF")
            
            logger.info(f"Extracted {len(images)} pages as images")
            
            # Check available vision models
            available_vision_models = []
            try:
                # Get all available models from Ollama
                logger.info("Attempting to connect to Ollama to list models...")
                models_response = self.vision_ocr_converter.ollama_client.client.list()
                logger.info(f"Ollama response: {models_response}")
                available_model_names = [model['name'] for model in models_response['models']]
                logger.info(f"Available model names: {available_model_names}")
                
                # Check which of our fallback models are available
                for model in self.fallback_vision_models:
                    if model in available_model_names:
                        available_vision_models.append(model)
                        logger.info(f"Found available vision model: {model}")
            except Exception as e:
                logger.error(f"Could not check vision model availability: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
            
            logger.info(f"Available vision models: {available_vision_models}")
            
            # Process each page
            all_text = []
            processed_pages = 0
            processing_method = "Unknown"
            
            for page_num, image_data in enumerate(images):
                logger.info(f"Processing page {page_num + 1}/{len(images)}")
                
                page_text = ""
                processing_method = "Unknown"
                
                # Try Vision OCR with multiple models if available
                if available_vision_models:
                    for model in available_vision_models:
                        try:
                            logger.info(f"Attempting Vision OCR with {model} for page {page_num + 1}")
                            
                            # Create a new vision converter with the current model
                            temp_vision_converter = VisionOcrConverter(
                                model=model,
                                use_hybrid_ocr=self.vision_ocr_converter.use_hybrid_ocr,
                                max_image_size=self.vision_ocr_converter.max_image_size,
                                use_grayscale=self.vision_ocr_converter.use_grayscale,
                                compression_quality=self.vision_ocr_converter.compression_quality,
                                timeout=self.vision_ocr_converter.timeout
                            )
                            
                            # Create a mock file stream for the image
                            import io
                            image_stream = io.BytesIO(image_data)
                            
                            # Create stream info for PNG image
                            image_stream_info = StreamInfo(
                                mimetype="image/png",
                                extension=".png"
                            )
                            
                                                         # Process with Vision OCR using chat() function
                             try:
                                 # Convert image to base64 for chat
                                 import base64
                                 image_base64 = base64.b64encode(image_data).decode('utf-8')
                                 logger.info(f"Image converted to base64, length: {len(image_base64)}")
                                 
                                 # Create chat message with image
                                 chat_message = "Please extract all text from this image. Return only the extracted text without any additional formatting or commentary."
                                 
                                 # Use chat() function for vision OCR with extended timeout
                                 logger.info(f"Attempting chat() with model {model} for page {page_num + 1}")
                                 
                                 # Set a longer timeout for vision processing (5 minutes)
                                 import requests
                                 from requests.adapters import HTTPAdapter
                                 from urllib3.util.retry import Retry
                                 
                                 # Create a session with longer timeout
                                 session = requests.Session()
                                 retry_strategy = Retry(
                                     total=3,
                                     backoff_factor=1,
                                     status_forcelist=[429, 500, 502, 503, 504],
                                 )
                                 adapter = HTTPAdapter(max_retries=retry_strategy)
                                 session.mount("http://", adapter)
                                 session.mount("https://", adapter)
                                 
                                 # Use direct HTTP call with longer timeout
                                 chat_url = "http://host.docker.internal:11434/api/chat"
                                 chat_payload = {
                                     "model": model,
                                     "messages": [
                                         {
                                             "role": "user",
                                             "content": chat_message,
                                             "images": [image_base64]
                                         }
                                     ]
                                 }
                                 
                                 logger.info(f"Sending vision request to {model} with 300s timeout...")
                                 response = session.post(chat_url, json=chat_payload, timeout=300)
                                 
                                 if response.status_code == 200:
                                     chat_response_data = response.json()
                                     if "error" in chat_response_data:
                                         logger.error(f"Model error: {chat_response_data['error']}")
                                         continue  # Try next model
                                     else:
                                         # Extract content from streaming response
                                         content_parts = []
                                         for line in response.text.strip().split('\n'):
                                             if line.strip():
                                                 try:
                                                     data = json.loads(line)
                                                     if 'message' in data and 'content' in data['message']:
                                                         content_parts.append(data['message']['content'])
                                                 except json.JSONDecodeError:
                                                     continue
                                         
                                         if content_parts:
                                             page_text = ''.join(content_parts).strip()
                                             processing_method = f"Vision OCR ({model})"
                                             logger.info(f"Vision OCR successful with {model} for page {page_num + 1}")
                                             break  # Success, no need to try other models
                                         else:
                                             logger.warning(f"Vision OCR with {model} returned empty content for page {page_num + 1}")
                                             continue  # Try next model
                                 else:
                                     logger.error(f"HTTP error {response.status_code}: {response.text}")
                                     continue  # Try next model
                                     page_text = chat_response.message.content.strip()
                                     processing_method = f"Vision OCR ({model})"
                                     logger.info(f"Vision OCR successful with {model} for page {page_num + 1}")
                                     break  # Success, no need to try other models
                                 else:
                                     logger.warning(f"Vision OCR with {model} returned empty result for page {page_num + 1}")
                                     
                             except Exception as chat_error:
                                 logger.error(f"Vision OCR chat() failed with {model} for page {page_num + 1}: {chat_error}")
                                 import traceback
                                 logger.error(f"Full traceback: {traceback.format_exc()}")
                                 continue  # Try next model
                                
                        except Exception as e:
                            logger.warning(f"Vision OCR with {model} failed for page {page_num + 1}: {e}")
                            continue  # Try next model
                
                # Fallback to Tesseract if all Vision OCR failed or unavailable
                if not page_text and self.fallback_to_tesseract:
                    try:
                        logger.info(f"Attempting Tesseract OCR for page {page_num + 1}")
                        page_text = self._extract_text_with_tesseract(image_data)
                        if page_text:
                            processing_method = "Tesseract OCR"
                            logger.info(f"Tesseract OCR successful for page {page_num + 1}")
                    except Exception as e:
                        logger.error(f"Tesseract OCR failed for page {page_num + 1}: {e}")
                
                if page_text.strip():
                    # Add page header and content
                    page_content = f"\n\n## Page {page_num + 1}\n\n{page_text.strip()}"
                    all_text.append(page_content)
                    processed_pages += 1
                
                logger.info(f"Completed page {page_num + 1}")
            
            # Combine all text
            combined_text = "\n".join(all_text) if all_text else ""
            
            # Add metadata
            combined_text += "\n\n---\n"
            combined_text += "### Processing Information\n"
            combined_text += f"**Processing Method:** {processing_method} (image-based PDF)\n"
            combined_text += f"**PDF Type:** Image-based\n"
            combined_text += f"**Pages Processed:** {processed_pages}/{len(images)}\n"
            if available_vision_models:
                combined_text += f"**Available Vision Models:** {', '.join(available_vision_models)}\n"
                combined_text += f"**Primary Vision Model:** {self.vision_ocr_converter.model}\n"
            else:
                combined_text += "**Vision Models:** Not available (used Tesseract fallback)\n"
            
            return DocumentConverterResult(markdown=combined_text)
            
        except Exception as e:
            logger.error(f"Image-based PDF processing failed: {e}")
            raise
    
    def _extract_text_with_tesseract(self, image_data: bytes) -> str:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Extracted text from the image
        """
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""

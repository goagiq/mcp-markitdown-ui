"""
Vision OCR Converter for MarkItDown
Uses Ollama vision models for OCR
"""

import os
import sys
import logging
import traceback
from typing import Optional, Dict, Any
from pathlib import Path

# Import from the same package
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

logger = logging.getLogger(__name__)


class OllamaVisionClient:
    """Client for Ollama vision models"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llava:7b"):
        self.base_url = base_url
        self.model = model
        self.session = None
        # Add client attribute for compatibility with advanced converters
        self.client = self
        self.host = base_url
        
    def _get_session(self):
        """Get or create requests session"""
        if self.session is None:
            import requests
            self.session = requests.Session()
        return self.session
    
    def chat(self, image_path: str, prompt: str = "Extract all text from this image. Return only the text content, no explanations.") -> str:
        """Send image to Ollama vision model and get text response"""
        try:
            import requests
            import base64
            
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "image": image_base64
                            }
                        ]
                    }
                ],
                "stream": False
            }
            
            # Make request
            session = self._get_session()
            response = session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            return result.get('message', {}).get('content', '')
            
        except Exception as e:
            logger.error(f"Error in Ollama vision chat: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def list(self):
        """List available models (for compatibility with advanced converters)"""
        try:
            import requests
            session = self._get_session()
            response = session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return {"models": []}


class VisionOcrConverter(DocumentConverter):
    """Vision OCR converter using Ollama vision models"""
    
    def __init__(self, model: str = "llava:7b", base_url: str = "http://localhost:11434", timeout: int = 300):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.client = OllamaVisionClient(base_url=base_url, model=model)
        # Add ollama_client attribute for compatibility with advanced converters
        self.ollama_client = self.client
    
    def convert(self, file_path: str, stream_info: Optional[StreamInfo] = None) -> DocumentConverterResult:
        """Convert image file to markdown using vision OCR"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Extract text using vision OCR
            text = self.client.chat(file_path)
            
            # Convert to markdown (simple conversion)
            markdown = f"# Extracted Text\n\n{text}\n"
            
            return DocumentConverterResult(markdown=markdown)
            
        except Exception as e:
            logger.error(f"Error in vision OCR conversion: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def convert_stream(self, stream, stream_info: Optional[StreamInfo] = None) -> DocumentConverterResult:
        """Convert stream to markdown using vision OCR"""
        # For now, save to temp file and use convert method
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(stream.read())
            temp_path = temp_file.name
        
        try:
            return self.convert(temp_path, stream_info)
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

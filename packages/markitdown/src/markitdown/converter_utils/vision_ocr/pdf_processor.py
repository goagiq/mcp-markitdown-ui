"""
PDF Processor for Vision OCR
Handles PDF analysis and conversion to images
"""

import os
import logging
from typing import List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PdfProcessor:
    """PDF processing utilities for vision OCR"""
    
    def __init__(self):
        pass
    
    def analyze_pdf_type(self, pdf_path: str) -> str:
        """Analyze if PDF is text-based or image-based"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            text_content = ""
            
            # Check first few pages for text content
            for page_num in range(min(3, len(doc))):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            
            doc.close()
            
            # If we have substantial text content, consider it text-based
            if len(text_content.strip()) > 100:
                return "text-based"
            else:
                return "image-based"
                
        except ImportError:
            logger.warning("PyMuPDF not available, assuming image-based PDF")
            return "image-based"
        except Exception as e:
            logger.error(f"Error analyzing PDF type: {e}")
            return "image-based"
    
    def pdf_to_images(self, pdf_path: str, output_dir: str, dpi: int = 300) -> List[str]:
        """Convert PDF pages to images"""
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import io
            
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Render page to image
                mat = fitz.Matrix(dpi/72, dpi/72)  # Scale factor
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Save image
                image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
                img.save(image_path, "PNG")
                image_paths.append(image_path)
            
            doc.close()
            return image_paths
            
        except ImportError:
            logger.error("PyMuPDF not available for PDF to image conversion")
            raise
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise


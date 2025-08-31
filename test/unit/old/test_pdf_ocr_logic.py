#!/usr/bin/env python3
"""
Test script for PDF OCR logic implementation.

This script tests the logic for:
1. Detecting if a PDF is text-based or image-based
2. Processing text-based PDFs normally
3. Converting image-based PDFs to PNG and using vision OCR
"""

import sys
import os
import logging
from pathlib import Path
from typing import BinaryIO, Any

# Add the markitdown package to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "markitdown" / "src"))

from markitdown._base_converter import DocumentConverterResult
from markitdown._stream_info import StreamInfo
from markitdown.converters._vision_ocr_converter import VisionOcrConverter
from markitdown.converters._pdf_converter import PdfConverter
from markitdown.converter_utils.vision_ocr.pdf_processor import (
    PdfProcessor, PdfType
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedPdfConverter:
    """
    Enhanced PDF converter that handles both text-based and image-based PDFs.
    
    Logic:
    1. If PDF is text-based, process normally using pdfminer
    2. Else, convert each page to PNG using PyMuPDF and use vision OCR
    """
    
    def __init__(self, vision_model: str = "llava:7b"):
        """
        Initialize the enhanced PDF converter.
        
        Args:
            vision_model: Ollama vision model to use for OCR
        """
        self.pdf_converter = PdfConverter()
        self.vision_ocr_converter = VisionOcrConverter(model=vision_model)
        self.pdf_processor = PdfProcessor()
        
        logger.info(f"Initialized EnhancedPdfConverter with vision model: {vision_model}")
    
    def convert_pdf(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any
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
                return self._process_text_based_pdf(file_stream, stream_info, **kwargs)
            else:
                logger.info("Processing image-based PDF with Vision OCR")
                return self._process_image_based_pdf(file_data, stream_info, **kwargs)
                
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise
    
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
            
            # Process each page with Vision OCR
            all_text = []
            total_processing_time = 0
            processed_pages = 0
            
            for page_num, image_data in enumerate(images):
                logger.info(f"Processing page {page_num + 1}/{len(images)} with Vision OCR")
                
                # Create a mock file stream for the image
                import io
                image_stream = io.BytesIO(image_data)
                
                # Create stream info for PNG image
                image_stream_info = StreamInfo(
                    mimetype="image/png",
                    extension=".png"
                )
                
                # Process with Vision OCR
                ocr_result = self.vision_ocr_converter.convert(
                    image_stream, image_stream_info, **kwargs
                )
                
                if ocr_result.markdown.strip():
                    # Add page header and content
                    page_text = f"\n\n## Page {page_num + 1}\n\n{ocr_result.markdown.strip()}"
                    all_text.append(page_text)
                    processed_pages += 1
                
                logger.info(f"Completed page {page_num + 1}")
            
            # Combine all text
            combined_text = "\n".join(all_text) if all_text else ""
            
            # Add metadata
            combined_text += "\n\n---\n"
            combined_text += "### Processing Information\n"
            combined_text += "**Processing Method:** Vision OCR (image-based PDF)\n"
            combined_text += f"**PDF Type:** {pdf_type.value}\n"
            combined_text += f"**Pages Processed:** {processed_pages}/{len(images)}\n"
            combined_text += f"**Vision Model:** {self.vision_ocr_converter.model}\n"
            
            return DocumentConverterResult(markdown=combined_text)
            
        except Exception as e:
            logger.error(f"Image-based PDF processing failed: {e}")
            raise


def test_pdf_conversion(pdf_path: str, output_path: str = None):
    """
    Test PDF conversion with the enhanced logic.
    
    Args:
        pdf_path: Path to PDF file to test
        output_path: Path to save output (optional)
    """
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return
        
        # Initialize converter
        converter = EnhancedPdfConverter()
        
        # Read file
        with open(pdf_path, 'rb') as f:
            file_data = f.read()
        
        # Create stream info
        stream_info = StreamInfo(
            mimetype="application/pdf",
            extension=".pdf"
        )
        
        # Create file stream
        import io
        file_stream = io.BytesIO(file_data)
        
        # Convert PDF
        logger.info(f"Converting PDF: {pdf_path}")
        result = converter.convert_pdf(file_stream, stream_info)
        
        # Save or display result
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.markdown)
            logger.info(f"Output saved to: {output_path}")
        else:
            print("\n" + "="*80)
            print("CONVERSION RESULT")
            print("="*80)
            print(result.markdown)
            print("="*80)
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


def main():
    """Main function to run tests."""
    # Test with the sample PDF
    test_pdf = "packages/markitdown/tests/test_files/test.pdf"
    
    if os.path.exists(test_pdf):
        logger.info(f"Testing with sample PDF: {test_pdf}")
        test_pdf_conversion(test_pdf, "test_output.md")
    else:
        logger.error(f"Sample PDF not found: {test_pdf}")
        logger.info("Please provide a PDF file path as argument")
        
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            output_path = sys.argv[2] if len(sys.argv) > 2 else "test_output.md"
            test_pdf_conversion(pdf_path, output_path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive test script for PDF OCR functionality.

This script tests:
1. PDF type detection
2. Text-based PDF processing
3. Image-based PDF processing (if available)
4. Enhanced PDF OCR converter
"""

import sys
import os
import logging
from pathlib import Path

# Add the markitdown package to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "markitdown" / "src"))

from markitdown._stream_info import StreamInfo
from markitdown.converters._enhanced_pdf_ocr_converter import EnhancedPdfOcrConverter
from markitdown.converter_utils.vision_ocr.pdf_processor import PdfProcessor, PdfType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pdf_type_detection(pdf_path: str):
    """Test PDF type detection."""
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        # Initialize PDF processor
        processor = PdfProcessor()
        
        # Read file
        with open(pdf_path, 'rb') as f:
            file_data = f.read()
        
        # Analyze PDF type
        pdf_type = processor.analyze_pdf_type(file_data)
        
        logger.info(f"PDF: {pdf_path}")
        logger.info(f"Detected type: {pdf_type.value}")
        
        # Get additional info
        info = processor.get_pdf_info(file_data)
        logger.info(f"Page count: {info.get('page_count', 'unknown')}")
        logger.info(f"File size: {info.get('file_size', 'unknown')} bytes")
        
        return pdf_type
        
    except Exception as e:
        logger.error(f"PDF type detection failed: {e}")
        return None


def test_enhanced_pdf_ocr(pdf_path: str, output_path: str = None):
    """Test the enhanced PDF OCR converter."""
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        # Initialize converter
        converter = EnhancedPdfOcrConverter()
        
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
        logger.info(f"Converting PDF with Enhanced PDF OCR: {pdf_path}")
        result = converter.convert(file_stream, stream_info)
        
        # Save or display result
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.markdown)
            logger.info(f"Output saved to: {output_path}")
        
        return result
        
    except Exception as e:
        logger.error(f"Enhanced PDF OCR test failed: {e}")
        return None


def main():
    """Main function to run comprehensive tests."""
    logger.info("Starting comprehensive PDF OCR tests...")
    
    # Test with the sample PDF
    test_pdf = "packages/markitdown/tests/test_files/test.pdf"
    
    if os.path.exists(test_pdf):
        logger.info("="*60)
        logger.info("TESTING SAMPLE PDF")
        logger.info("="*60)
        
        # Test PDF type detection
        pdf_type = test_pdf_type_detection(test_pdf)
        
        # Test enhanced PDF OCR
        result = test_enhanced_pdf_ocr(test_pdf, "comprehensive_test_output.md")
        
        if result:
            logger.info("✅ Sample PDF test completed successfully")
        else:
            logger.error("❌ Sample PDF test failed")
    else:
        logger.error(f"Sample PDF not found: {test_pdf}")
    
    # Test with additional PDFs if provided
    if len(sys.argv) > 1:
        additional_pdfs = sys.argv[1:]
        
        for i, pdf_path in enumerate(additional_pdfs):
            logger.info("="*60)
            logger.info(f"TESTING ADDITIONAL PDF {i+1}: {pdf_path}")
            logger.info("="*60)
            
            # Test PDF type detection
            pdf_type = test_pdf_type_detection(pdf_path)
            
            # Test enhanced PDF OCR
            output_path = f"comprehensive_test_output_{i+1}.md"
            result = test_enhanced_pdf_ocr(pdf_path, output_path)
            
            if result:
                logger.info(f"✅ Additional PDF {i+1} test completed successfully")
            else:
                logger.error(f"❌ Additional PDF {i+1} test failed")
    
    logger.info("="*60)
    logger.info("COMPREHENSIVE TESTS COMPLETED")
    logger.info("="*60)


if __name__ == "__main__":
    main()

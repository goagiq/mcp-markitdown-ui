#!/usr/bin/env python3
"""
Test script to verify PDF type detection and processing logic.
"""

import sys
import os
import logging
from pathlib import Path

# Add the markitdown package to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "markitdown" / "src"))

from markitdown.converter_utils.vision_ocr.pdf_processor import PdfProcessor, PdfType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pdf_type_detection(pdf_path: str):
    """Test PDF type detection."""
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return
        
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
        logger.error(f"Test failed: {e}")
        raise


def main():
    """Main function to run tests."""
    # Test with the sample PDF
    test_pdf = "packages/markitdown/tests/test_files/test.pdf"
    
    if os.path.exists(test_pdf):
        logger.info("Testing PDF type detection...")
        test_pdf_type_detection(test_pdf)
    else:
        logger.error(f"Sample PDF not found: {test_pdf}")
        
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            test_pdf_type_detection(pdf_path)


if __name__ == "__main__":
    main()

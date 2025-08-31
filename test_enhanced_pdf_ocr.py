#!/usr/bin/env python3
"""
Test script for the Enhanced PDF OCR Converter.
"""

import sys
import os
import logging
from pathlib import Path

# Add the markitdown package to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "markitdown" / "src"))

from markitdown._stream_info import StreamInfo
from markitdown.converters._enhanced_pdf_ocr_converter import EnhancedPdfOcrConverter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_enhanced_pdf_ocr(pdf_path: str, output_path: str = None):
    """
    Test the enhanced PDF OCR converter.
    
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
        else:
            print("\n" + "="*80)
            print("ENHANCED PDF OCR CONVERSION RESULT")
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
        logger.info(f"Testing Enhanced PDF OCR with sample PDF: {test_pdf}")
        test_enhanced_pdf_ocr(test_pdf, "enhanced_pdf_ocr_output.md")
    else:
        logger.error(f"Sample PDF not found: {test_pdf}")
        logger.info("Please provide a PDF file path as argument")
        
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            output_path = sys.argv[2] if len(sys.argv) > 2 else "enhanced_pdf_ocr_output.md"
            test_enhanced_pdf_ocr(pdf_path, output_path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Direct test script for processing the specific PDF file.
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


def test_pdf_processing():
    """Test processing the specific PDF file."""
    try:
        # Initialize converter
        converter = EnhancedPdfOcrConverter()
        
        # PDF file path
        pdf_path = "input/Publication of Unclassified Intelligence Analysis Products IPM.pdf"
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return
        
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
        result = converter.convert(file_stream, stream_info)
        
        # Save result
        output_path = "output/test_direct_output.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.markdown)
        
        logger.info(f"Output saved to: {output_path}")
        logger.info(f"Output length: {len(result.markdown)} characters")
        
        # Show first 500 characters
        preview = result.markdown[:500] + "..." if len(result.markdown) > 500 else result.markdown
        logger.info(f"Preview: {preview}")
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    test_pdf_processing()

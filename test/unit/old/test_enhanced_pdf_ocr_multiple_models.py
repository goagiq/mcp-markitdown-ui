#!/usr/bin/env python3
"""
Test script for Enhanced PDF OCR Converter with multiple vision model fallback.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the markitdown package to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "markitdown" / "src"))

from markitdown._stream_info import StreamInfo
from markitdown.converters._enhanced_pdf_ocr_converter import EnhancedPdfOcrConverter

def test_enhanced_pdf_ocr_multiple_models():
    """Test the enhanced PDF OCR converter with multiple vision model fallback."""
    
    # PDF file to test
    pdf_path = "input/Publication of Unclassified Intelligence Analysis Products IPM.pdf"
    
    try:
        # Initialize the enhanced converter
        logger.info("Initializing Enhanced PDF OCR Converter...")
        converter = EnhancedPdfOcrConverter(
            vision_model="llava:7b",  # Primary model (may not be available)
            fallback_to_tesseract=True
        )
        
        # Create stream info
        stream_info = StreamInfo(
            mimetype="application/pdf",
            extension=".pdf"
        )
        
        # Test the converter
        logger.info(f"Testing with PDF: {pdf_path}")
        
        with open(pdf_path, 'rb') as file_stream:
            # Check if converter accepts the file
            if converter.accepts(file_stream, stream_info):
                logger.info("Converter accepts the PDF file")
                
                # Reset file position
                file_stream.seek(0)
                
                # Convert the PDF
                logger.info("Starting PDF conversion...")
                result = converter.convert(file_stream, stream_info)
                
                # Check the result
                if result and result.markdown:
                    logger.info(f"Conversion successful! Extracted {len(result.markdown)} characters")
                    
                    # Save the result
                    output_path = "output/Publication of Unclassified Intelligence Analysis Products IPM_multiple_models.markdown"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result.markdown)
                    
                    logger.info(f"Result saved to: {output_path}")
                    
                    # Show a preview of the result
                    preview = result.markdown[:500] + "..." if len(result.markdown) > 500 else result.markdown
                    logger.info(f"Preview: {preview}")
                    
                else:
                    logger.error("Conversion failed - no result or empty markdown")
                    
            else:
                logger.error("Converter does not accept the PDF file")
                
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_pdf_ocr_multiple_models()




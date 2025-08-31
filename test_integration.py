#!/usr/bin/env python3
"""
Integration test for the Enhanced PDF OCR Converter within MarkItDown.
"""

import sys
import os
import logging
from pathlib import Path

# Add the markitdown package to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "markitdown" / "src"))

from markitdown import MarkItDown
from markitdown.converters import EnhancedPdfOcrConverter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_integration():
    """Test integration of Enhanced PDF OCR Converter with MarkItDown."""
    try:
        # Initialize MarkItDown with the enhanced converter
        markitdown = MarkItDown()
        
        # Add the enhanced PDF OCR converter
        enhanced_converter = EnhancedPdfOcrConverter()
        markitdown.register_converter(enhanced_converter)
        
        logger.info("✅ Enhanced PDF OCR Converter integrated successfully")
        
        # Test with sample PDF
        test_pdf = "packages/markitdown/tests/test_files/test.pdf"
        
        if os.path.exists(test_pdf):
            logger.info(f"Testing integration with: {test_pdf}")
            
            # Convert using MarkItDown
            result = markitdown.convert(test_pdf)
            
            if result:
                logger.info("✅ Integration test completed successfully")
                logger.info(f"Output length: {len(result.markdown)} characters")
                
                # Save output
                with open("integration_test_output.md", "w", encoding="utf-8") as f:
                    f.write(result.markdown)
                logger.info("Output saved to: integration_test_output.md")
                
                return True
            else:
                logger.error("❌ Integration test failed - no output")
                return False
        else:
            logger.error(f"Sample PDF not found: {test_pdf}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False


def main():
    """Main function."""
    logger.info("Starting integration test...")
    
    success = test_integration()
    
    if success:
        logger.info("🎉 All integration tests passed!")
    else:
        logger.error("💥 Integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

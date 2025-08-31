#!/usr/bin/env python3
"""
Test script for vision OCR with ffmpeg and locally hosted Ollama.
"""

import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the markitdown package to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "markitdown" / "src"))

from markitdown._stream_info import StreamInfo
from markitdown.converters._enhanced_pdf_ocr_converter import EnhancedPdfOcrConverter

def test_ffmpeg_availability():
    """Test if ffmpeg is available in the container."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("ffmpeg is available!")
            logger.info(f"ffmpeg version: {result.stdout.split('ffmpeg version')[1].split()[0]}")
            return True
        else:
            logger.error("ffmpeg is not available")
            return False
    except FileNotFoundError:
        logger.error("ffmpeg command not found")
        return False

def test_ollama_connection():
    """Test connection to locally hosted Ollama."""
    try:
        import requests
        response = requests.get('http://host.docker.internal:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json()
            logger.info(f"Successfully connected to Ollama! Found {len(models.get('models', []))} models")
            for model in models.get('models', []):
                if 'vision' in model.get('name', '').lower() or 'llava' in model.get('name', '').lower():
                    logger.info(f"Vision model found: {model['name']}")
            return True
        else:
            logger.error(f"Failed to connect to Ollama: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error connecting to Ollama: {e}")
        return False

def test_vision_ocr():
    """Test the enhanced PDF OCR converter with vision models."""
    
    # PDF file to test
    pdf_path = "input/Publication of Unclassified Intelligence Analysis Products IPM.pdf"
    
    try:
        # Initialize the enhanced converter
        logger.info("Initializing Enhanced PDF OCR Converter...")
        converter = EnhancedPdfOcrConverter(
            vision_model="minicpm-v:latest",  # Use an available vision model
            fallback_to_tesseract=False  # Disable Tesseract fallback to focus on vision OCR
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
                    output_path = "output/Publication of Unclassified Intelligence Analysis Products IPM_vision_ocr_test.markdown"
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

def main():
    """Main test function."""
    logger.info("=== Testing Vision OCR with ffmpeg and locally hosted Ollama ===")
    
    # Test 1: Check ffmpeg availability
    logger.info("\n1. Testing ffmpeg availability...")
    ffmpeg_available = test_ffmpeg_availability()
    
    # Test 2: Check Ollama connection
    logger.info("\n2. Testing Ollama connection...")
    ollama_connected = test_ollama_connection()
    
    # Test 3: Test vision OCR
    if ffmpeg_available and ollama_connected:
        logger.info("\n3. Testing vision OCR...")
        test_vision_ocr()
    else:
        logger.error("Skipping vision OCR test due to missing dependencies")
        if not ffmpeg_available:
            logger.error("- ffmpeg is not available")
        if not ollama_connected:
            logger.error("- Cannot connect to Ollama")

if __name__ == "__main__":
    main()

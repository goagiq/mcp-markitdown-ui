#!/usr/bin/env python3
"""
Debug script to test vision OCR timeout issues
"""

import os
import sys
import logging
import base64
import requests
import json
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vision_model(model_name, timeout=120):
    """Test a specific vision model"""
    try:
        # Create a simple test image (10x10 pixel PNG)
        # This is a minimal valid PNG
        test_image_data = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\r'     # IHDR chunk length
            b'IHDR'               # IHDR chunk type
            b'\x00\x00\x00\n'     # width (10)
            b'\x00\x00\x00\n'     # height (10)
            b'\x08\x02\x00\x00\x00'  # bit depth, color type, compression, filter, interlace
            b'\x00\x00\x00\x00'   # CRC placeholder
            b'\x00\x00\x00\t'     # IDAT chunk length
            b'IDAT'               # IDAT chunk type
            b'\x08\x1d\x01\x01\x00\x00\x00'  # minimal image data
            b'\x00\x00\x00\x00'   # CRC placeholder
            b'\x00\x00\x00\x00'   # IEND chunk length
            b'IEND'               # IEND chunk type
            b'\xaeB`\x82'         # IEND CRC
        )
        
        # Convert to base64
        image_base64 = base64.b64encode(test_image_data).decode('utf-8')
        logger.info(f"Testing {model_name} with {len(image_base64)} char base64 image")
        
        # Test chat with vision model
        url = "http://host.docker.internal:11434/api/chat"
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "What do you see in this image?",
                    "images": [image_base64]
                }
            ]
        }
        
        logger.info(f"Sending request to {model_name} with {timeout}s timeout...")
        start_time = time.time()
        
        response = requests.post(url, json=payload, timeout=timeout)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Response received in {elapsed_time:.2f}s")
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                logger.error(f"Model error: {result['error']}")
                return False
            else:
                logger.info(f"Success! Response: {result}")
                return True
        else:
            logger.error(f"HTTP error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout after {timeout}s for {model_name}")
        return False
    except Exception as e:
        logger.error(f"Error with {model_name}: {e}")
        return False

def main():
    """Test all available vision models"""
    logger.info("=== Vision Model Timeout Test ===")
    
    # Test different models with different timeouts
    models_to_test = [
        ("minicpm-v:latest", 60),
        ("llava:latest", 60),
        ("llama3.2-vision:latest", 120),
    ]
    
    for model_name, timeout in models_to_test:
        logger.info(f"\n--- Testing {model_name} (timeout: {timeout}s) ---")
        success = test_vision_model(model_name, timeout)
        if success:
            logger.info(f"✓ {model_name} works!")
            break
        else:
            logger.error(f"✗ {model_name} failed")
    
    logger.info("\n=== Test Complete ===")

if __name__ == "__main__":
    main()




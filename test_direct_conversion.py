#!/usr/bin/env python3
"""
Direct test of the advanced PDF OCR converter
"""
import os
import sys
import traceback

# Add the packages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/markitdown/src'))

def test_direct_conversion():
    """Test the conversion directly"""
    try:
        from markitdown.converters._advanced_optimized_pdf_ocr_converter import AdvancedOptimizedPdfOcrConverter
        from markitdown._stream_info import StreamInfo
        
        pdf_path = "input/Publication_of_Unclassified_Intelligence_Analysis_Products_IPM.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}")
            return
        
        print(f"Testing direct conversion of: {pdf_path}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")
        
        # Create converter
        converter = AdvancedOptimizedPdfOcrConverter()
        
        # Read file data
        with open(pdf_path, 'rb') as f:
            file_data = f.read()
        
        # Create stream info
        stream_info = StreamInfo(
            filename=os.path.basename(pdf_path),
            mimetype="application/pdf",
            extension=".pdf"
        )
        
        print("Starting conversion...")
        
        # Convert
        result = converter.convert(file_data, stream_info)
        
        print("Conversion completed!")
        print(f"Result length: {len(result.markdown)} characters")
        print(f"Preview: {result.markdown[:200]}...")
        
        # Save result
        output_path = "output/test_direct_conversion.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.markdown)
        
        print(f"Result saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_conversion()

#!/usr/bin/env python3
"""
Test script for web conversion endpoint
"""
import requests
import os
import json

def test_web_conversion():
    """Test the web conversion endpoint"""
    url = "http://127.0.0.1:8200/convert"
    pdf_path = "input/Publication_of_Unclassified_Intelligence_Analysis_Products_IPM.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print(f"Testing conversion of: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            print("Sending conversion request...")
            
            response = requests.post(url, files=files, timeout=300)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("Conversion successful!")
                print(f"Output filename: {result.get('filename', 'N/A')}")
                print(f"Message: {result.get('message', 'N/A')}")
                
                # Check if output file was created
                output_dir = "output"
                if os.path.exists(output_dir):
                    output_files = os.listdir(output_dir)
                    print(f"Output files: {output_files}")
            else:
                print(f"Conversion failed: {response.text}")
                
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_conversion()

#!/usr/bin/env python3
"""
Test script for MarkItDown MCP Server
Tests both the MCP protocol and REST API endpoints
"""

import requests
import json
import time
import subprocess
import sys
import os

def test_rest_api():
    """Test REST API endpoints"""
    base_url = "http://127.0.0.1:8200"
    
    print("Testing REST API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test supported formats endpoint
    try:
        response = requests.get(f"{base_url}/supported_formats")
        print(f"Supported formats: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Supported formats failed: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return False
    
    return True

def test_mcp_protocol():
    """Test MCP protocol endpoint"""
    base_url = "http://127.0.0.1:8200"
    
    print("\nTesting MCP protocol endpoint...")
    
    # Test tools/list
    try:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(f"{base_url}/mcp", json=request)
        result = response.json()
        print(f"Tools list: {response.status_code}")
        print(f"Available tools: {[tool['name'] for tool in result.get('result', {}).get('tools', [])]}")
    except Exception as e:
        print(f"Tools list failed: {e}")
        return False
    
    # Test list_supported_formats tool
    try:
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_supported_formats",
                "arguments": {}
            }
        }
        
        response = requests.post(f"{base_url}/mcp", json=request)
        result = response.json()
        print(f"List formats tool: {response.status_code}")
        if 'result' in result:
            print(f"Result: {result['result']['content'][0]['text']}")
    except Exception as e:
        print(f"List formats tool failed: {e}")
        return False
    
    return True

def start_server():
    """Start the MCP server"""
    print("Starting MarkItDown MCP Server...")
    
    # Check if deployment.py exists
    if not os.path.exists("deployment.py"):
        print("Error: deployment.py not found")
        return None
    
    # Start the server
    try:
        process = subprocess.Popen([
            sys.executable, "deployment.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        return process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def main():
    """Main test function"""
    print("MarkItDown MCP Server Test")
    print("=" * 40)
    
    # Start the server
    server_process = start_server()
    if not server_process:
        print("Failed to start server")
        return
    
    try:
        # Test REST API
        rest_success = test_rest_api()
        
        # Test MCP protocol
        mcp_success = test_mcp_protocol()
        
        print("\n" + "=" * 40)
        print("Test Results:")
        print(f"REST API: {'PASS' if rest_success else 'FAIL'}")
        print(f"MCP Protocol: {'PASS' if mcp_success else 'FAIL'}")
        
        if rest_success and mcp_success:
            print("\n✅ All tests passed! MCP server is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()

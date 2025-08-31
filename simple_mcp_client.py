#!/usr/bin/env python3
"""
Simple Working MCP Client
Demonstrates the correct way to connect to the MarkItDown MCP server
"""

import requests
import json


def mcp_client():
    base_url = "http://127.0.0.1:8200/mcp"
    
    print("=== MarkItDown MCP Client ===")
    print(f"Connecting to: {base_url}")
    
    # Step 1: Establish session with GET request
    print("\n1. Establishing session...")
    try:
        session_response = requests.get(
            base_url,
            headers={"Accept": "text/event-stream"}
        )
        session_id = session_response.headers.get('mcp-session-id')
        print(f"✅ Session established: {session_id}")
    except Exception as e:
        print(f"❌ Failed to establish session: {e}")
        return
    
    # Step 2: List available tools
    print("\n2. Listing available tools...")
    try:
        response = requests.post(
            base_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-ID": session_id
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Debug - Full response: {json.dumps(result, indent=2)}")
            tools = result.get("result", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            
            # Step 3: Test a tool call
            if tools:
                print(f"\n3. Testing tool: {tools[0]['name']}")
                test_tool_call(base_url, tools[0]['name'], session_id)
        else:
            print(f"❌ Failed to list tools: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")


def test_tool_call(base_url, tool_name, session_id):
    """Test calling a specific tool"""
    try:
        if tool_name == "list_supported_formats":
            # This tool doesn't need arguments
            response = requests.post(
                base_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {}
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "MCP-Session-ID": session_id
                }
            )
        else:
            # For other tools, we'd need proper arguments
            print(f"   (Skipping {tool_name} - needs specific arguments)")
            return
            
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                content = result["result"].get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        print(f"   ✅ Result: {item['text'][:100]}...")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error calling tool: {e}")


if __name__ == "__main__":
    mcp_client()

#!/usr/bin/env python3
"""
Test production MCP server Ollama integration diagnostics
"""

import requests
import json
import os

MCP_URL = os.getenv("WILDEDITOR_MCP_ROOT_URL", "http://127.0.0.1:8001")
MCP_KEY = os.environ["WILDEDITOR_MCP_KEY"]

def test_mcp_description():
    """Test description generation and analyze the response"""
    print("🧪 Testing MCP Description Generation on Production...")
    
    # Make request
    response = requests.post(
        f"{MCP_URL}/mcp",
        headers={
            "X-API-Key": MCP_KEY,
            "Content-Type": "application/json"
        },
        json={
            "id": "diagnostic-test",
            "method": "tools/call",
            "params": {
                "name": "generate_region_description",
                "arguments": {
                    "region_name": "Shadowmere Lake",
                    "terrain_theme": "mystical_waters",
                    "description_style": "poetic",
                    "description_length": "brief"
                }
            }
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Extract the result text
        if 'result' in data and 'content' in data['result']:
            content = data['result']['content'][0]['text']
            
            # Parse the Python dict string
            try:
                # It's a string representation of a dict, need to eval it carefully
                import ast
                result_dict = ast.literal_eval(content)
                
                print("\n📊 Analysis:")
                print(f"AI Provider: {result_dict.get('ai_provider', 'unknown')}")
                print(f"Word Count: {result_dict.get('word_count', 'N/A')}")
                print(f"Quality Score: {result_dict.get('suggested_quality_score', 'N/A')}")
                
                # Show first 200 chars of description
                desc = result_dict.get('generated_description', '')
                print(f"\n📝 Description Preview:")
                print(desc[:200] + "..." if len(desc) > 200 else desc)
                
                # Diagnostic info
                print(f"\n🔍 Diagnostic Info:")
                if result_dict.get('ai_provider') == 'template':
                    print("❌ Using template fallback (no AI provider worked)")
                    print("Possible reasons:")
                    print("  1. OpenAI API key not set or invalid")
                    print("  2. Ollama not accessible from container")
                    print("  3. Environment variables not properly configured")
                elif result_dict.get('ai_provider') == 'ollama_fallback':
                    print("✅ Using Ollama fallback (OpenAI failed, Ollama worked)")
                elif result_dict.get('ai_provider') == 'openai':
                    print("✅ Using OpenAI primary provider")
                
            except Exception as e:
                print(f"Error parsing result: {e}")
                print(f"Raw content: {content[:500]}")
    else:
        print(f"❌ Request failed: {response.text}")

def test_ollama_on_server():
    """Test if Ollama is accessible on the production server"""
    print("\n🌐 Testing Ollama Service on Production Server...")
    
    # We can't directly test localhost:11434 from here, but we can 
    # infer from the MCP behavior
    print("Note: Can't directly test Ollama from outside the server")
    print("The MCP server would use Ollama if:")
    print("  1. OLLAMA_BASE_URL is set (should be http://localhost:11434)")
    print("  2. OLLAMA_MODEL is set (should be llama3.2:1b)")
    print("  3. Ollama service is running on the server")
    print("  4. The model is installed (ollama pull llama3.2:1b)")

if __name__ == "__main__":
    print("🚀 Production Ollama Integration Diagnostic\n")
    test_mcp_description()
    test_ollama_on_server()
    
    print("\n💡 Recommendations:")
    print("1. Check GitHub Secrets are set correctly:")
    print("   - OLLAMA_BASE_URL = http://localhost:11434")
    print("   - OLLAMA_MODEL = llama3.2:1b")
    print("2. SSH to server and verify Ollama:")
    print("   - curl http://localhost:11434/api/tags")
    print("   - docker exec wildeditor-mcp env | grep OLLAMA")
    print("3. Check container logs:")
    print("   - docker logs wildeditor-mcp --tail 50")

#!/usr/bin/env python3
"""
Test Ollama integration with MCP service
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any

# Add MCP source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'mcp', 'src'))

from services.ai_service import AIService, AIProvider

async def test_ollama_fallback_configuration():
    """Test that Ollama fallback is properly configured"""
    print("🔧 Testing Ollama Fallback Configuration...")
    
    # Set environment variables for fallback chain (OpenAI -> Ollama -> Template)
    os.environ["AI_PROVIDER"] = "openai"  # Primary provider
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"  # Fallback
    os.environ["OLLAMA_MODEL"] = "llama3.2:1b"  # Fallback model
    os.environ.pop("OPENAI_API_KEY", None)  # Remove OpenAI key to force fallback
    
    # Create AI service instance
    ai_service = AIService()
    
    # Check provider is set to OpenAI (primary)
    if ai_service.provider != AIProvider.OPENAI:
        print(f"❌ Expected primary provider 'openai', got '{ai_service.provider}'")
        return False
    
    print(f"✅ Primary provider configured: {ai_service.provider}")
    
    # Check that primary provider is not available (should fallback)
    if ai_service.is_available():
        print("❌ Primary AI service should not be available without API key")
        return False
    
    print("✅ Primary AI service unavailable (will trigger fallback)")
    
    # Check Ollama environment variables are set
    ollama_url = os.environ.get("OLLAMA_BASE_URL")
    ollama_model = os.environ.get("OLLAMA_MODEL")
    
    print(f"📋 Fallback URL: {ollama_url}")
    print(f"📋 Fallback Model: {ollama_model}")
    
    return True

async def test_fallback_chain():
    """Test the OpenAI -> Ollama -> Template fallback chain"""
    print("\n🎯 Testing Fallback Chain (OpenAI -> Ollama -> Template)...")
    
    # Set environment variables to test fallback
    os.environ["AI_PROVIDER"] = "openai"  # Primary
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"  # Fallback
    os.environ["OLLAMA_MODEL"] = "llama3.2:1b"  # Fallback model
    os.environ.pop("OPENAI_API_KEY", None)  # Force primary to fail
    
    # Create AI service instance
    ai_service = AIService()
    
    # Primary should not be available
    if ai_service.is_available():
        print("❌ Primary provider should not be available (no API key)")
        return False
    
    print("✅ Primary provider unavailable, will test fallback")
    
    # Test generation - should fallback to Ollama
    try:
        print("🔄 Testing fallback generation...")
        
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        result = await ai_service.generate_description(
            region_name="Test Mystical Grove",
            terrain_theme="enchanted_forest", 
            style="poetic",
            length="brief"
        )
        
        if not result:
            print("❌ No result returned - fallback chain may have failed")
            return False
        
        # Check if result came from Ollama fallback
        ai_provider = result.get('ai_provider', '')
        if ai_provider != 'ollama_fallback':
            print(f"❌ Expected 'ollama_fallback', got '{ai_provider}'")
            return False
        
        print("✅ Ollama fallback generation successful!")
        print(f"📝 Generated description: {result['generated_description'][:200]}...")
        print(f"📊 Word count: {result.get('word_count', 'N/A')}")
        print(f"🤖 AI Provider: {ai_provider}")
        
        # Check metadata
        if 'metadata' in result:
            print(f"🏷️  Quality Score: {result['metadata'].get('quality_score', 'N/A')}")
            print(f"🔍 Key Features: {result.get('key_features', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during fallback generation: {e}")
        return False

async def test_ollama_connectivity():
    """Test direct Ollama connectivity"""
    print("\n🌐 Testing Direct Ollama Connectivity...")
    
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test /api/tags endpoint
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status != 200:
                    print(f"❌ Ollama /api/tags returned status {response.status}")
                    return False
                
                data = await response.json()
                models = data.get("models", [])
                
                print(f"✅ Ollama is responsive (found {len(models)} models)")
                
                # Check for our specific model
                llama_model = next((m for m in models if m["name"] == "llama3.2:1b"), None)
                if not llama_model:
                    print("❌ llama3.2:1b model not found in Ollama")
                    return False
                
                print(f"✅ Found llama3.2:1b model (size: {llama_model['size']} bytes)")
                
            # Test a simple generation request
            test_request = {
                "model": "llama3.2:1b",
                "prompt": "Hello, this is a test. Please respond with 'Test successful'.",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 50
                }
            }
            
            async with session.post("http://localhost:11434/api/generate", 
                                   json=test_request) as response:
                if response.status != 200:
                    print(f"❌ Ollama generation returned status {response.status}")
                    text = await response.text()
                    print(f"Response body: {text}")
                    return False
                
                data = await response.json()
                response_text = data.get("response", "")
                
                print(f"✅ Direct Ollama generation successful")
                print(f"📝 Response: {response_text[:100]}...")
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing Ollama connectivity: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Ollama Integration Tests\n")
    
    # Run tests
    tests = [
        ("Ollama Connectivity", test_ollama_connectivity),
        ("Ollama Fallback Configuration", test_ollama_fallback_configuration), 
        ("Fallback Chain (OpenAI->Ollama->Template)", test_fallback_chain),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            success = await test_func()
            results.append((test_name, success))
            print(f"\n{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
            
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ollama integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
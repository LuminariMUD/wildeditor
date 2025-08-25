#!/usr/bin/env python3
"""
Test AI providers independently to diagnose issues
"""

import os
import asyncio
import sys
import json

# Test different scenarios locally
async def test_scenario(scenario_name, env_setup):
    """Test a specific scenario with given environment setup"""
    print(f"\n🧪 Testing: {scenario_name}")
    print("Environment setup:", json.dumps(env_setup, indent=2))
    
    # Clear and set environment
    for key in ['AI_PROVIDER', 'OPENAI_API_KEY', 'OLLAMA_BASE_URL', 'OLLAMA_MODEL']:
        os.environ.pop(key, None)
    
    for key, value in env_setup.items():
        if value:
            os.environ[key] = value
    
    # Import after setting environment
    sys.path.insert(0, 'apps/mcp/src')
    from services.ai_service import AIService
    
    # Create service and test
    service = AIService()
    print(f"Provider detected: {service.provider}")
    print(f"Service available: {service.is_available()}")
    
    # Try to generate
    result = await service.generate_description(
        region_name="Test Region",
        terrain_theme="forest",
        style="brief",
        length="brief"
    )
    
    if result:
        print(f"✅ Generation successful!")
        print(f"AI Provider used: {result.get('ai_provider', 'unknown')}")
    else:
        print(f"❌ Generation returned None (template fallback expected)")
    
    return result

async def main():
    print("🚀 AI Provider Diagnostic Tests\n")
    
    scenarios = [
        # Scenario 1: No configuration (should use template)
        ("No Configuration", {}),
        
        # Scenario 2: Only Ollama configured
        ("Ollama Only", {
            "AI_PROVIDER": "ollama",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "llama3.2:1b"
        }),
        
        # Scenario 3: OpenAI primary with Ollama fallback (no API key)
        ("OpenAI Primary (no key) + Ollama Fallback", {
            "AI_PROVIDER": "openai",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "llama3.2:1b"
        }),
        
        # Scenario 4: OpenAI with invalid key + Ollama fallback
        ("OpenAI (invalid key) + Ollama Fallback", {
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-invalid-test-key",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "llama3.2:1b"
        })
    ]
    
    for name, env in scenarios:
        try:
            result = await test_scenario(name, env)
        except Exception as e:
            print(f"❌ Error in scenario: {e}")
    
    print("\n" + "="*50)
    print("📊 Summary:")
    print("="*50)
    print("\nFor production to work correctly:")
    print("1. OpenAI API key must be valid (starts with 'sk-')")
    print("2. Ollama must be running on server at localhost:11434")
    print("3. GitHub Secrets must be properly set")
    print("4. Docker container must have network access to Ollama")
    
    print("\n🔍 Current local Ollama status:")
    import subprocess
    try:
        result = subprocess.run(['curl', '-s', 'http://localhost:11434/api/tags'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            models = data.get('models', [])
            if models:
                print(f"✅ Ollama is running locally with {len(models)} model(s)")
                for model in models:
                    print(f"   - {model['name']}")
            else:
                print("⚠️ Ollama is running but no models installed")
        else:
            print("❌ Ollama is not accessible locally")
    except Exception as e:
        print(f"❌ Could not check Ollama: {e}")

if __name__ == "__main__":
    asyncio.run(main())
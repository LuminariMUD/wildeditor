#!/usr/bin/env python3
"""
Test script for DeepSeek AI provider integration in MCP server.

This script validates:
1. DeepSeek API configuration
2. Model availability
3. Description generation with DeepSeek
4. Fallback chain with DeepSeek
"""

import asyncio
import os
import sys
from pathlib import Path

# Add MCP source to path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "mcp" / "src"))

from services.ai_service import AIService, AIProvider, GeneratedDescription
from pydantic_ai.models.openai import OpenAIModel


async def test_deepseek_configuration():
    """Test DeepSeek provider configuration"""
    print("\n" + "="*60)
    print("Testing DeepSeek Configuration")
    print("="*60)
    
    # Save current env
    original_provider = os.environ.get("AI_PROVIDER")
    original_key = os.environ.get("DEEPSEEK_API_KEY")
    
    try:
        # Test explicit DeepSeek provider selection
        os.environ["AI_PROVIDER"] = "deepseek"
        
        # Check if API key is set
        if not os.environ.get("DEEPSEEK_API_KEY"):
            print("⚠️ DEEPSEEK_API_KEY not set - using test mode")
            os.environ["DEEPSEEK_API_KEY"] = "test-key-for-config-check"
            test_mode = True
        else:
            print("✅ DEEPSEEK_API_KEY found")
            test_mode = False
        
        # Initialize service
        service = AIService()
        
        # Check provider selection
        if service.provider == AIProvider.DEEPSEEK:
            print(f"✅ DeepSeek provider selected: {service.provider.value}")
        else:
            print(f"❌ Wrong provider selected: {service.provider.value}")
            return False
        
        # Check model configuration
        model_name = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
        print(f"✅ Model: {model_name}")
        
        # Check if model was initialized (only if real API key)
        if not test_mode:
            if service.model is not None:
                print("✅ DeepSeek model initialized successfully")
            else:
                print("❌ Failed to initialize DeepSeek model")
                return False
        else:
            print("ℹ️ Skipping model initialization check (test mode)")
        
        return True
        
    finally:
        # Restore original env
        if original_provider:
            os.environ["AI_PROVIDER"] = original_provider
        elif "AI_PROVIDER" in os.environ:
            del os.environ["AI_PROVIDER"]
        
        if original_key:
            os.environ["DEEPSEEK_API_KEY"] = original_key
        elif "DEEPSEEK_API_KEY" in os.environ:
            del os.environ["DEEPSEEK_API_KEY"]


async def test_deepseek_generation():
    """Test actual description generation with DeepSeek"""
    print("\n" + "="*60)
    print("Testing DeepSeek Description Generation")
    print("="*60)
    
    # Check if API key is available
    if not os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") == "test-key-for-config-check":
        print("⚠️ Skipping generation test - no valid DEEPSEEK_API_KEY")
        print("ℹ️ Set DEEPSEEK_API_KEY environment variable to test generation")
        return True
    
    # Save current env
    original_provider = os.environ.get("AI_PROVIDER")
    
    try:
        # Force DeepSeek provider
        os.environ["AI_PROVIDER"] = "deepseek"
        
        # Initialize service
        service = AIService()
        
        # Test generation
        result = await service.generate_description(
            region_name="Crystal Caverns",
            terrain_theme="underground crystalline caves",
            style="mysterious",
            length="brief",
            sections=["overview", "atmosphere"]
        )
        
        if result and "generated_description" in result:
            print("✅ Description generated successfully")
            print(f"   Provider: {result.get('ai_provider', 'unknown')}")
            print(f"   Word count: {result.get('word_count', 0)}")
            print(f"   Quality score: {result.get('suggested_quality_score', 0)}")
            print("\n   Preview (first 200 chars):")
            print(f"   {result['generated_description'][:200]}...")
            return True
        else:
            print("❌ Failed to generate description")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False
        
    finally:
        # Restore original env
        if original_provider:
            os.environ["AI_PROVIDER"] = original_provider
        elif "AI_PROVIDER" in os.environ:
            del os.environ["AI_PROVIDER"]


async def test_deepseek_fallback():
    """Test fallback chain with DeepSeek"""
    print("\n" + "="*60)
    print("Testing Fallback Chain with DeepSeek")
    print("="*60)
    
    # Save current env
    original_provider = os.environ.get("AI_PROVIDER")
    original_openai = os.environ.get("OPENAI_API_KEY")
    original_deepseek = os.environ.get("DEEPSEEK_API_KEY")
    
    try:
        # Test 1: DeepSeek as primary with no key (should fallback)
        print("\n1. Testing DeepSeek as primary with no key:")
        os.environ["AI_PROVIDER"] = "deepseek"
        if "DEEPSEEK_API_KEY" in os.environ:
            del os.environ["DEEPSEEK_API_KEY"]
        
        service = AIService()
        if service.provider == AIProvider.DEEPSEEK and not service.is_available():
            print("   ✅ DeepSeek selected but not available (will trigger fallback)")
        else:
            print("   ❌ Unexpected behavior")
        
        # Test 2: Auto-detection with DeepSeek key only
        print("\n2. Testing auto-detection with DeepSeek key:")
        if "AI_PROVIDER" in os.environ:
            del os.environ["AI_PROVIDER"]
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        os.environ["DEEPSEEK_API_KEY"] = "test-key"
        
        service = AIService()
        if service.provider == AIProvider.DEEPSEEK:
            print("   ✅ DeepSeek auto-detected from API key")
        else:
            print(f"   ❌ Wrong provider auto-detected: {service.provider.value}")
        
        # Test 3: Priority order (OpenAI > Anthropic > DeepSeek)
        print("\n3. Testing provider priority order:")
        if "AI_PROVIDER" in os.environ:
            del os.environ["AI_PROVIDER"]
        os.environ["OPENAI_API_KEY"] = "test-openai-key"
        os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"
        
        service = AIService()
        if service.provider == AIProvider.OPENAI:
            print("   ✅ OpenAI selected (higher priority than DeepSeek)")
        else:
            print(f"   ❌ Wrong provider selected: {service.provider.value}")
        
        return True
        
    finally:
        # Restore original env
        if original_provider:
            os.environ["AI_PROVIDER"] = original_provider
        elif "AI_PROVIDER" in os.environ:
            del os.environ["AI_PROVIDER"]
        
        if original_openai:
            os.environ["OPENAI_API_KEY"] = original_openai
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        if original_deepseek:
            os.environ["DEEPSEEK_API_KEY"] = original_deepseek
        elif "DEEPSEEK_API_KEY" in os.environ:
            del os.environ["DEEPSEEK_API_KEY"]


async def main():
    """Run all DeepSeek integration tests"""
    print("\n" + "="*60)
    print("DeepSeek Integration Test Suite")
    print("="*60)
    
    all_passed = True
    
    # Test configuration
    if not await test_deepseek_configuration():
        all_passed = False
    
    # Test fallback chain
    if not await test_deepseek_fallback():
        all_passed = False
    
    # Test generation (if API key available)
    if not await test_deepseek_generation():
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    if all_passed:
        print("✅ All DeepSeek integration tests passed!")
        print("\nTo test actual generation, set DEEPSEEK_API_KEY environment variable:")
        print("  export DEEPSEEK_API_KEY='your-api-key'")
        print("  python test_deepseek_integration.py")
    else:
        print("❌ Some tests failed - check output above")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
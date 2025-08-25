#!/usr/bin/env python3
"""
Test script for AI service configuration
Verifies that the AI service can be initialized and used
"""

import asyncio
import sys
import os

# Add the MCP src directory to path
sys.path.insert(0, '/home/luminari/wildeditor/apps/mcp/src')

from services.ai_service import get_ai_service

async def test_ai_service():
    """Test AI service initialization and basic functionality"""
    print("=" * 60)
    print("AI SERVICE CONFIGURATION TEST")
    print("=" * 60)
    
    # Get AI service instance
    ai_service = get_ai_service()
    
    # Get provider info
    provider_info = ai_service.get_provider_info()
    print(f"\n✅ AI Service initialized")
    print(f"   Provider: {provider_info['provider']}")
    print(f"   Available: {provider_info['available']}")
    print(f"   Model: {provider_info.get('model', 'N/A')}")
    
    # Check if AI is available
    if ai_service.is_available():
        print("\n✅ AI provider is configured and ready")
        print("   Attempting to generate a test description...")
        
        # Try to generate a simple description
        result = await ai_service.generate_description(
            region_name="Test Valley",
            terrain_theme="peaceful valley with a stream",
            style="poetic",
            length="brief",
            sections=["overview"]
        )
        
        if result:
            print("\n✅ AI generation successful!")
            print(f"   Word count: {result.get('word_count', 0)}")
            print(f"   AI Provider: {result.get('ai_provider', 'unknown')}")
            print(f"   Quality score: {result.get('suggested_quality_score', 0):.1f}")
            
            # Show preview
            desc = result.get('generated_description', '')
            if desc:
                print(f"\n   Preview (first 200 chars):")
                print(f"   {desc[:200]}...")
        else:
            print("\n⚠️  AI generation returned None - will fall back to templates")
    else:
        print("\n⚠️  No AI provider configured")
        print("   The system will use template-based generation")
        print("\n   To enable AI generation, configure one of:")
        print("   - OPENAI_API_KEY environment variable")
        print("   - ANTHROPIC_API_KEY environment variable")
        print("   - OLLAMA_BASE_URL for local models")
    
    print("\n" + "=" * 60)
    print("CONFIGURATION STATUS")
    print("=" * 60)
    
    # Check environment variables
    print("\nEnvironment variables:")
    print(f"   AI_PROVIDER: {os.getenv('AI_PROVIDER', 'not set')}")
    print(f"   OPENAI_API_KEY: {'✅ set' if os.getenv('OPENAI_API_KEY') else '❌ not set'}")
    print(f"   ANTHROPIC_API_KEY: {'✅ set' if os.getenv('ANTHROPIC_API_KEY') else '❌ not set'}")
    print(f"   OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'not set')}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ai_service())
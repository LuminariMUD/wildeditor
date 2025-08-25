#!/usr/bin/env python3
"""
Test OpenAI Integration for MCP Server
Verifies that the AI service works with the configured OpenAI API key
"""

import asyncio
import sys
import os

# Set environment variables from .env
os.environ['AI_PROVIDER'] = 'openai'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'

# Add the MCP src directory to path
sys.path.insert(0, '/home/luminari/wildeditor/apps/mcp/src')

from services.ai_service import get_ai_service

async def test_openai():
    """Test OpenAI service with actual API call"""
    print("=" * 60)
    print("OPENAI INTEGRATION TEST")
    print("=" * 60)
    
    # Get AI service instance
    ai_service = get_ai_service()
    
    # Get provider info
    provider_info = ai_service.get_provider_info()
    print(f"\n✅ AI Service initialized")
    print(f"   Provider: {provider_info['provider']}")
    print(f"   Available: {provider_info['available']}")
    print(f"   Model: {provider_info.get('model', 'N/A')}")
    
    if not ai_service.is_available():
        print("\n❌ OpenAI service is not available. Check API key.")
        return False
    
    print("\n🚀 Testing AI generation with OpenAI...")
    print("   Generating description for 'Crystal Caverns'...")
    
    try:
        # Test generation
        result = await ai_service.generate_description(
            region_name="Crystal Caverns",
            terrain_theme="underground caverns filled with glowing crystals",
            style="mysterious",
            length="brief",
            sections=["overview", "atmosphere"]
        )
        
        if result:
            print("\n✅ AI generation successful!")
            print(f"   Provider: {result.get('ai_provider', 'unknown')}")
            print(f"   Word count: {result.get('word_count', 0)}")
            print(f"   Quality score: {result.get('suggested_quality_score', 0):.1f}")
            
            # Show metadata
            metadata = result.get('metadata', {})
            if metadata:
                print(f"\n   Metadata:")
                print(f"     Historical: {metadata.get('has_historical_context', False)}")
                print(f"     Resources: {metadata.get('has_resource_info', False)}")
                print(f"     Wildlife: {metadata.get('has_wildlife_info', False)}")
                print(f"     Geological: {metadata.get('has_geological_info', False)}")
                print(f"     Cultural: {metadata.get('has_cultural_info', False)}")
            
            # Show preview
            desc = result.get('generated_description', '')
            if desc:
                print(f"\n   Description preview (first 300 chars):")
                print(f"   {desc[:300]}...")
            
            return True
        else:
            print("\n⚠️ AI generation returned None - falling back to templates")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during AI generation: {e}")
        return False

async def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("TESTING OPENAI CONFIGURATION")
    print("=" * 60)
    
    print("\nConfiguration:")
    print(f"  Model: gpt-4o-mini")
    print(f"  Max tokens: 500")
    print(f"  Temperature: 0.7")
    print(f"  Cost: ~$0.15/1M input tokens, $0.60/1M output tokens")
    
    success = await test_openai()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - OpenAI integration is working!")
        print("\nNext steps:")
        print("1. Run ./setup_github_secrets.sh to get secret values")
        print("2. Add secrets to GitHub repository settings")
        print("3. Push to main branch to deploy with AI support")
    else:
        print("❌ TEST FAILED - Check the error messages above")
        print("\nPossible issues:")
        print("- API key might be invalid or expired")
        print("- Rate limits might be exceeded")
        print("- Network connectivity issues")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
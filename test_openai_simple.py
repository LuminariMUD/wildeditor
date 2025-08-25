#!/usr/bin/env python3
"""
Simple OpenAI API test to verify the key works
"""

import asyncio
from openai import AsyncOpenAI

async def test_openai():
    """Test OpenAI API directly"""
    
    # Initialize client
    # Get API key from environment
    import os
    api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
    
    client = AsyncOpenAI(
        api_key=api_key
    )
    
    print("Testing OpenAI API key...")
    
    try:
        # Simple completion test
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, the API key works!' if you can hear me."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        message = response.choices[0].message.content
        print(f"✅ API Response: {message}")
        print(f"   Model: {response.model}")
        print(f"   Usage: {response.usage.total_tokens} tokens")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai())
    
    if success:
        print("\n✅ OpenAI API key is valid and working!")
    else:
        print("\n❌ OpenAI API key test failed")
        print("The key might be:")
        print("- Invalid or expired")
        print("- Missing required permissions")
        print("- Rate limited")
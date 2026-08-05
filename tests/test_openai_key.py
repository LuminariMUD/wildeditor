#!/usr/bin/env python3
"""
Test if the OpenAI API key from the debug endpoint works
"""

import os
from openai import OpenAI

# Set the API key from what we saw in debug
api_key = input("Enter the OpenAI API key (sk-p...): ").strip()

if not api_key.startswith("sk-"):
    print("❌ Invalid key format (should start with sk-)")
    exit(1)

print(f"Testing OpenAI API key: {api_key[:8]}...")

try:
    client = OpenAI(api_key=api_key)
    
    # Try a simple completion
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'test successful' if you can hear me"}
        ],
        max_tokens=10
    )
    
    print("✅ OpenAI API key is valid!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ OpenAI API key test failed: {e}")
    if "invalid_api_key" in str(e):
        print("The API key is invalid or expired")
    elif "insufficient_quota" in str(e):
        print("The API key has no credits/quota")
    else:
        print("Other error - check the error message above")
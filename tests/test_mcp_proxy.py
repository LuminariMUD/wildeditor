#!/usr/bin/env python3
"""
Test the MCP proxy endpoint
"""

import requests
import json

# Configuration
BACKEND_URL = "http://luminarimud.com:8000/api"
API_KEY = "0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"

def test_generate_description():
    """Test the generate-description endpoint"""
    print("Testing MCP proxy endpoint...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "region_vnum": 9999002,
        "region_name": "Test Forest",
        "region_type": 1,
        "terrain_theme": "forest",
        "description_style": "poetic",
        "description_length": "moderate",
        "include_sections": ["overview", "atmosphere"],
        "user_prompt": "A mystical forest with ancient trees"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/mcp/generate-description",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_generate_description()
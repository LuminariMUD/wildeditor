#!/usr/bin/env python3
import requests
import json

# Get the region first
region_response = requests.get(
    "http://luminarimud.com:8000/api/regions/9999001",
    headers={"Authorization": "Bearer 0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"}
)

if region_response.status_code != 200:
    print(f"Failed to get region: {region_response.status_code}")
    exit(1)

region = region_response.json()
description = region.get('region_description', '')

if not description:
    print("Region has no description")
    exit(1)

print(f"Description length: {len(description)}")
print(f"First 100 chars: {description[:100]}...")

# Call the MCP tool via backend proxy
response = requests.post(
    "http://luminarimud.com:8000/api/mcp/call-tool",
    headers={
        "Authorization": "Bearer 0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu",
        "Content-Type": "application/json"
    },
    json={
        "tool_name": "generate_hints_from_description",
        "arguments": {
            "region_vnum": 9999001,
            "region_name": region.get('name', 'Test Region'),
            "description": description,
            "target_hint_count": 20,
            "include_profile": True
        }
    }
)

print(f"\nMCP Response status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        result = data.get('result', {})
        
        # Parse the text result if it's a string
        if isinstance(result, dict) and 'text' in result:
            try:
                import ast
                parsed = ast.literal_eval(result['text'])
                print(f"\nHints generated: {len(parsed.get('hints', []))}")
                print(f"Total hints found: {parsed.get('total_hints_found', 0)}")
                
                # Show first few hints
                for i, hint in enumerate(parsed.get('hints', [])[:3]):
                    print(f"\nHint {i+1}:")
                    print(f"  Category: {hint.get('category')}")
                    print(f"  Text: {hint.get('text')[:100]}...")
                    print(f"  Priority: {hint.get('priority')}")
            except Exception as e:
                print(f"Failed to parse result: {e}")
                print(f"Raw result: {result}")
        else:
            print(f"Result: {result}")
    else:
        print(f"Error: {data.get('error')}")
else:
    print(f"Failed: {response.text}")
#!/usr/bin/env python3
"""Test the updated hint generation with AI-powered hint creation"""

import requests
import json
import time

# API configuration
API_URL = "http://luminarimud.com:8000/api"
API_KEY = "0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"
TEST_VNUM = 9999001  # Thornwall Thickets

def test_hint_generation():
    """Test the full hint generation workflow"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Get the region with description
    print("Step 1: Fetching region data...")
    region_response = requests.get(
        f"{API_URL}/regions/{TEST_VNUM}",
        headers=headers
    )
    
    if region_response.status_code != 200:
        print(f"Failed to get region: {region_response.status_code}")
        print(region_response.text)
        return
    
    region = region_response.json()
    description = region.get('region_description', '')
    
    print(f"Region: {region.get('name', 'Unknown')}")
    print(f"Description exists: {bool(description)}")
    print(f"Description length: {len(description)}")
    
    if not description:
        print("\nNo description found. Generate one first.")
        return
    
    print("\nFirst 200 chars of description:")
    print(description[:200] + "...")
    
    # Step 2: Call the MCP tool to generate hints
    print("\n" + "="*50)
    print("Step 2: Generating hints from description...")
    print("="*50)
    
    mcp_request = {
        "tool_name": "generate_hints_from_description",
        "arguments": {
            "region_vnum": TEST_VNUM,
            "region_name": region.get('name', 'Test Region'),
            "description": description,
            "target_hint_count": 15,
            "include_profile": True
        }
    }
    
    print("Calling MCP tool...")
    start_time = time.time()
    
    mcp_response = requests.post(
        f"{API_URL}/mcp/call-tool",
        headers=headers,
        json=mcp_request
    )
    
    elapsed = time.time() - start_time
    print(f"Response received in {elapsed:.1f} seconds")
    print(f"Status code: {mcp_response.status_code}")
    
    if mcp_response.status_code != 200:
        print("Failed to generate hints:")
        print(mcp_response.text)
        return
    
    data = mcp_response.json()
    
    if not data.get('success'):
        print(f"Error: {data.get('error', 'Unknown error')}")
        return
    
    result = data.get('result', {})
    
    # Parse the result
    if isinstance(result, dict) and 'text' in result:
        # Legacy format - parse the text
        try:
            import ast
            parsed = ast.literal_eval(result['text'])
            hints = parsed.get('hints', [])
            print(f"\nParsed {len(hints)} hints from text format")
        except Exception as e:
            print(f"Failed to parse text result: {e}")
            print("Raw result:", result)
            return
    elif isinstance(result, dict) and 'hints' in result:
        # Direct format
        hints = result.get('hints', [])
        print(f"\nReceived {len(hints)} hints directly")
    else:
        print("Unexpected result format:", result)
        return
    
    # Step 3: Display the generated hints
    print("\n" + "="*50)
    print("Generated Hints:")
    print("="*50)
    
    if not hints:
        print("No hints generated!")
        return
    
    # Group hints by category
    by_category = {}
    for hint in hints:
        category = hint.get('category') or hint.get('hint_category', 'unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(hint)
    
    # Display hints by category
    for category, category_hints in by_category.items():
        print(f"\n{category.upper()} ({len(category_hints)} hints):")
        print("-" * 40)
        
        for i, hint in enumerate(category_hints[:2], 1):  # Show first 2 of each category
            text = hint.get('text') or hint.get('hint_text', '')
            priority = hint.get('priority', 5)
            
            # Check for formatting issues
            has_headers = any(header in text for header in ['OVERVIEW:', 'FLORA:', 'FAUNA:', 'GEOGRAPHY:'])
            
            print(f"\n  Hint #{i} (Priority: {priority}):")
            print(f"  {text[:150]}...")
            
            if has_headers:
                print("  ⚠️  WARNING: Contains header formatting!")
    
    # Step 4: Check if hints are properly formatted
    print("\n" + "="*50)
    print("Quality Check:")
    print("="*50)
    
    total_hints = len(hints)
    hints_with_headers = sum(1 for h in hints if any(
        header in (h.get('text') or h.get('hint_text', ''))
        for header in ['OVERVIEW:', 'FLORA:', 'FAUNA:', 'GEOGRAPHY:', 'CLIMATE:', 'HISTORY:']
    ))
    
    print(f"Total hints generated: {total_hints}")
    print(f"Hints with headers/formatting: {hints_with_headers}")
    print(f"Clean hints: {total_hints - hints_with_headers}")
    
    if hints_with_headers > 0:
        print("\n⚠️  Some hints still contain headers/formatting!")
        print("These should be clean descriptive sentences.")
    else:
        print("\n✓ All hints appear to be clean descriptive sentences!")
    
    # Show profile if generated
    if isinstance(result, dict) and 'profile' in result:
        profile = result['profile']
        if profile:
            print("\n" + "="*50)
            print("Region Profile:")
            print("="*50)
            print(f"Theme: {profile.get('overall_theme', 'N/A')}")
            print(f"Mood: {profile.get('dominant_mood', 'N/A')}")
            print(f"Style: {profile.get('description_style', 'N/A')}")
            print(f"Complexity: {profile.get('complexity_level', 'N/A')}")
    
    # Step 5: Check if description is still intact
    print("\n" + "="*50)
    print("Step 5: Verifying region description is intact...")
    print("="*50)
    
    verify_response = requests.get(
        f"{API_URL}/regions/{TEST_VNUM}",
        headers=headers
    )
    
    if verify_response.status_code == 200:
        verify_region = verify_response.json()
        verify_description = verify_region.get('region_description', '')
        
        if verify_description == description:
            print("✓ Description is intact!")
        elif not verify_description:
            print("⚠️  WARNING: Description has been cleared!")
        else:
            print("⚠️  WARNING: Description has changed!")
            print(f"Original length: {len(description)}")
            print(f"Current length: {len(verify_description)}")
    else:
        print(f"Failed to verify: {verify_response.status_code}")

if __name__ == "__main__":
    test_hint_generation()
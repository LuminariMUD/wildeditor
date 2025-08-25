#!/usr/bin/env python3
"""
Test script for region description API endpoints
Usage: python3 test_region_descriptions.py YOUR_API_KEY
"""

import sys
import json
import requests
from datetime import datetime

# Get API key from command line
if len(sys.argv) < 2:
    print("Usage: python3 test_region_descriptions.py YOUR_API_KEY")
    print("Please provide your API key as an argument")
    sys.exit(1)

API_KEY = sys.argv[1]
BASE_URL = "https://api.wildedit.luminarimud.com/api"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_create_region_with_description():
    """Test POST /api/regions with description fields"""
    print("\n=== Testing POST /api/regions with description ===")
    
    # Generate a unique vnum for testing
    test_vnum = 9000000 + int(datetime.now().timestamp()) % 100000
    
    region_data = {
        "vnum": test_vnum,
        "zone_vnum": 1,
        "name": "Test Region with Description",
        "region_type": 1,  # Geographic
        "coordinates": [
            {"x": 100, "y": 100},
            {"x": 150, "y": 100},
            {"x": 150, "y": 150},
            {"x": 100, "y": 150},
            {"x": 100, "y": 100}
        ],
        "region_props": 0,
        "region_reset_data": "",
        # New description fields
        "region_description": "TEST REGION DESCRIPTION\n\nThis is a test region created to verify the description API functionality.\n\nKey Features:\n- Automated test region\n- Contains sample description text\n- Tests all description metadata fields",
        "description_style": "practical",
        "description_length": "brief",
        "has_historical_context": True,
        "has_resource_info": False,
        "has_wildlife_info": True,
        "has_geological_info": False,
        "has_cultural_info": True,
        "ai_agent_source": "test_script",
        "description_quality_score": 7.5,
        "requires_review": False,
        "is_approved": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/regions/", json=region_data, headers=HEADERS)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Region created successfully!")
            print(f"   VNUM: {result['vnum']}")
            print(f"   Name: {result['name']}")
            print(f"   Description exists: {result.get('region_description') is not None}")
            print(f"   Description style: {result.get('description_style')}")
            print(f"   Description length type: {result.get('description_length')}")
            print(f"   Quality score: {result.get('description_quality_score')}")
            print(f"   Has historical context: {result.get('has_historical_context')}")
            print(f"   AI source: {result.get('ai_agent_source')}")
            return result['vnum']
        else:
            print(f"❌ Failed to create region: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating region: {e}")
        return None

def test_update_region_description(vnum):
    """Test PUT /api/regions/{vnum} with description updates"""
    print(f"\n=== Testing PUT /api/regions/{vnum} with description update ===")
    
    update_data = {
        "region_description": "UPDATED TEST DESCRIPTION\n\nThis description has been updated via the PUT endpoint.\n\nNew Features:\n- Updated content\n- Modified metadata\n- Testing description versioning",
        "description_style": "mysterious",
        "description_length": "moderate",
        "has_geological_info": True,
        "description_quality_score": 8.2,
        "is_approved": False,
        "requires_review": True
    }
    
    try:
        response = requests.put(f"{BASE_URL}/regions/{vnum}", json=update_data, headers=HEADERS)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Region updated successfully!")
            print(f"   Description updated: {result.get('region_description', '').startswith('UPDATED')}")
            print(f"   New style: {result.get('description_style')}")
            print(f"   New length type: {result.get('description_length')}")
            print(f"   New quality score: {result.get('description_quality_score')}")
            print(f"   Description version: {result.get('description_version')}")
            print(f"   Requires review: {result.get('requires_review')}")
            return True
        else:
            print(f"❌ Failed to update region: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error updating region: {e}")
        return False

def test_get_region_with_description(vnum):
    """Test GET /api/regions/{vnum} returns full description"""
    print(f"\n=== Testing GET /api/regions/{vnum} for full description ===")
    
    try:
        response = requests.get(f"{BASE_URL}/regions/{vnum}", headers={"Authorization": f"Bearer {API_KEY}"})
        
        if response.status_code == 200:
            result = response.json()
            desc = result.get('region_description', '')
            print(f"✅ Region retrieved successfully!")
            print(f"   Description length: {len(desc)} chars")
            print(f"   Description preview: {desc[:100]}..." if desc else "   No description")
            print(f"   All metadata fields present: {all(key in result for key in ['description_style', 'description_length', 'description_version'])}")
            return True
        else:
            print(f"❌ Failed to get region: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting region: {e}")
        return False

def test_list_regions_performance():
    """Test GET /api/regions with different include_descriptions options"""
    print("\n=== Testing GET /api/regions performance ===")
    
    tests = [
        ("false", "Without descriptions"),
        ("summary", "With summaries"),
        ("true", "With full descriptions")
    ]
    
    for include_desc, label in tests:
        try:
            response = requests.get(
                f"{BASE_URL}/regions?include_descriptions={include_desc}", 
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_size = len(response.content)
                first_region = data[0] if data else {}
                
                print(f"\n   {label}:")
                print(f"   ✅ Response size: {response_size:,} bytes")
                print(f"   ✅ Has region_description field: {'region_description' in first_region}")
                print(f"   ✅ Has description_summary field: {'description_summary' in first_region}")
            else:
                print(f"   ❌ Failed ({label}): {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error ({label}): {e}")

def cleanup_test_region(vnum):
    """Delete the test region"""
    print(f"\n=== Cleaning up test region {vnum} ===")
    
    try:
        response = requests.delete(f"{BASE_URL}/regions/{vnum}", headers=HEADERS)
        
        if response.status_code == 204:
            print(f"✅ Test region deleted successfully")
            return True
        else:
            print(f"⚠️  Could not delete test region: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Error deleting test region: {e}")
        return False

def main():
    print("=" * 60)
    print("REGION DESCRIPTION API TEST")
    print("=" * 60)
    
    # Test creating a region with description
    test_vnum = test_create_region_with_description()
    
    if test_vnum:
        # Test updating the region's description
        test_update_region_description(test_vnum)
        
        # Test getting the region with full description
        test_get_region_with_description(test_vnum)
        
        # Test list performance
        test_list_regions_performance()
        
        # Clean up
        cleanup_test_region(test_vnum)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
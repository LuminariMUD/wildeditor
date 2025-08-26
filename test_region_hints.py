#!/usr/bin/env python3
"""
Test script for the Region Hints System
Creates a test region (Crystal Caverns) and generates hints from its description
"""

import json
import requests
import asyncio
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://luminarimud.com:8000/api"
MCP_URL = "http://luminarimud.com:8001/mcp"
MCP_API_KEY = "xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="
BACKEND_API_KEY = "0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"

# Test region configuration
TEST_REGION = {
    "vnum": 9999001,
    "name": "The Crystal Caverns",
    "zone_vnum": 999,
    "region_type": 1,  # Geographic
    "coordinates": [
        {"x": -100, "y": -100},
        {"x": -100, "y": -50},
        {"x": -50, "y": -50},
        {"x": -50, "y": -100}
    ],
    "region_props": 0,
    "region_description": """THE CRYSTAL CAVERNS COMPREHENSIVE DESCRIPTION

OVERVIEW:
The Crystal Caverns are a magnificent underground wonder, where nature has crafted a cathedral of living crystal over millennia. Massive crystalline formations stretch from floor to ceiling, their surfaces catching and refracting light in endless prismatic displays. The air itself seems to shimmer with ethereal energy, and a profound sense of ancient magic permeates every chamber.

GEOGRAPHY:
The caverns extend deep into the mountain's heart, forming a complex network of interconnected chambers and passages. The main gallery soars to heights of over 100 feet, supported by natural crystal columns that have grown together over eons. Smaller grottos branch off in all directions, each containing unique crystal formations - from delicate needle-like structures to massive geodes that could house entire buildings. Underground springs have carved smooth channels through the crystal floor, their waters crystal-clear and mysteriously luminescent.

FLORA:
Despite the absence of sunlight, life thrives in these depths. Bioluminescent fungi cling to the crystal surfaces, their soft blue-green glow providing a gentle, ever-present light. Strange pale flowers with translucent petals grow in clusters where mineral-rich water seeps through cracks. Patches of phosphorescent moss carpet the areas where crystal gives way to stone, pulsing with a slow, hypnotic rhythm that seems synchronized with some deeper heartbeat of the earth.

FAUNA:
The caverns host a unique ecosystem adapted to the crystalline environment. Crystal bats with translucent wing membranes roost in the higher reaches, their echolocation creating haunting melodies as it resonates through the crystals. Blind cave fish swim in the underground pools, their scales reflecting the ambient light like living jewels. Occasionally, the rare crystal spider can be spotted, its body seemingly carved from living diamond, spinning webs that shimmer like strings of stars.

ATMOSPHERE:
An otherworldly silence dominates the caverns, broken only by the musical ping of water droplets and the occasional harmonic resonance when air currents cause the crystals to sing. The temperature remains constant and cool, with a slight humidity that makes the air feel alive and refreshing. During certain times, when conditions are just right, the entire cavern system resonates with a deep, almost inaudible hum that visitors feel more than hear.

MYSTICAL ELEMENTS:
Ancient runic inscriptions can be found carved into some of the oldest crystal formations, their meaning lost to time but still pulsing with faint magical energy. Local legends speak of the Crystal Heart, a massive gem supposedly hidden in the deepest chamber, said to be the source of the caverns' mystical properties. Visitors often report experiencing vivid dreams and visions while resting within the caverns, and items left overnight sometimes acquire strange crystalline growths.

SEASONAL VARIATIONS:
While the caverns maintain a constant temperature, they respond to the seasons above in subtle ways. In spring, new crystal growth appears as tiny points of light. Summer brings an increase in the bioluminescent activity. Autumn sees the formation of crystal flowers that bloom for just a few weeks. Winter causes the crystals to ring with different tones, creating an ethereal winter symphony.

RESOURCES:
The caverns contain valuable crystal specimens prized by mages and artificers. The spring water has mild healing properties. Certain fungi can be harvested for alchemical purposes. The crystal formations themselves could provide materials for magical focuses, though harvesting them is said to anger the cavern's guardian spirits.""",
    "description_style": "mysterious",
    "description_length": "extensive",
    "has_historical_context": True,
    "has_resource_info": True,
    "has_wildlife_info": True,
    "has_geological_info": True,
    "has_cultural_info": True,
    "description_quality_score": 9.5,
    "is_approved": True,
    "ai_agent_source": "test_script"
}


def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool and return the result"""
    request_data = {
        "id": f"test-{tool_name}",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    headers = {
        "X-API-Key": MCP_API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{MCP_URL}/request",
        headers=headers,
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        if "result" in data and "content" in data["result"]:
            result_text = data["result"]["content"][0]["text"]
            try:
                # Try to parse as JSON first
                return json.loads(result_text)
            except json.JSONDecodeError:
                # If that fails, try eval for dict-like strings
                try:
                    import ast
                    return ast.literal_eval(result_text)
                except:
                    return {"text": result_text}
    return {"error": f"Failed to call {tool_name}: {response.status_code}"}


def test_create_region():
    """Step 1: Create the test region"""
    print("\n=== Step 1: Creating Test Region ===")
    
    headers = {
        "Authorization": f"Bearer {BACKEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/regions/",
        headers=headers,
        json=TEST_REGION
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ Region created successfully: {TEST_REGION['name']} (VNUM: {TEST_REGION['vnum']})")
        return True
    elif response.status_code == 409:
        print(f"ℹ️ Region already exists, updating it...")
        # Try to update existing region
        response = requests.put(
            f"{BACKEND_URL}/regions/{TEST_REGION['vnum']}",
            headers=headers,
            json=TEST_REGION
        )
        if response.status_code == 200:
            print(f"✅ Region updated successfully")
            return True
    
    print(f"❌ Failed to create region: {response.status_code}")
    if response.text:
        print(f"   Error: {response.text}")
    return False


def test_generate_hints():
    """Step 2: Generate hints from description"""
    print("\n=== Step 2: Generating Hints from Description ===")
    
    result = call_mcp_tool("generate_hints_from_description", {
        "region_vnum": TEST_REGION["vnum"],
        "region_name": TEST_REGION["name"],
        "description": TEST_REGION["region_description"],
        "target_hint_count": 20,
        "include_profile": True
    })
    
    if "error" in result:
        print(f"❌ Failed to generate hints: {result['error']}")
        return None
    
    print(f"✅ Generated {result.get('total_hints_found', 0)} hints")
    print(f"   Returning top {len(result.get('hints', []))} hints")
    
    # Display sample hints by category
    if "hints" in result:
        categories = {}
        for hint in result["hints"]:
            cat = hint.get("category", "unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(hint)
        
        print("\n   Hints by Category:")
        for cat, hints in categories.items():
            print(f"   - {cat}: {len(hints)} hints")
            if hints:
                print(f"     Sample: \"{hints[0]['text'][:80]}...\"")
    
    # Display profile if generated
    if "profile" in result and result["profile"]:
        profile = result["profile"]
        print("\n   Generated Profile:")
        print(f"   - Mood: {profile.get('dominant_mood', 'unknown')}")
        print(f"   - Style: {profile.get('description_style', 'unknown')}")
        print(f"   - Characteristics: {', '.join(profile.get('key_characteristics', []))}")
    
    return result


def test_store_hints(hints_data):
    """Step 3: Store hints in database"""
    print("\n=== Step 3: Storing Hints in Database ===")
    
    if not hints_data or "hints" not in hints_data:
        print("❌ No hints to store")
        return False
    
    # Store via API directly (since MCP tool would also call API)
    headers = {
        "Authorization": f"Bearer {BACKEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Format hints for API
    formatted_hints = []
    for hint in hints_data["hints"]:
        formatted_hint = {
            "hint_category": hint["category"],
            "hint_text": hint["text"],
            "priority": hint.get("priority", 5),
            "weather_conditions": hint.get("weather_conditions", ["clear", "cloudy", "rainy"])
            # "ai_agent_id": "test_script"  # Commented out - column not yet in production
        }
        
        # Add optional fields if present
        if "seasonal_weight" in hint:
            formatted_hint["seasonal_weight"] = hint["seasonal_weight"]
        if "time_of_day_weight" in hint:
            formatted_hint["time_of_day_weight"] = hint["time_of_day_weight"]
            
        formatted_hints.append(formatted_hint)
    
    # Store hints
    response = requests.post(
        f"{BACKEND_URL}/regions/{TEST_REGION['vnum']}/hints",
        headers=headers,
        json={"hints": formatted_hints}
    )
    
    if response.status_code in [200, 201]:
        stored = response.json()
        print(f"✅ Successfully stored {len(stored)} hints")
    else:
        print(f"❌ Failed to store hints: {response.status_code}")
        if response.text:
            print(f"   Error: {response.text}")
        return False
    
    # Store profile if available
    if hints_data.get("profile"):
        profile = hints_data["profile"]
        response = requests.post(
            f"{BACKEND_URL}/regions/{TEST_REGION['vnum']}/profile",
            headers=headers,
            json=profile
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Successfully stored region profile")
        else:
            print(f"⚠️ Failed to store profile: {response.status_code}")
    
    return True


def test_retrieve_hints():
    """Step 4: Retrieve and verify stored hints"""
    print("\n=== Step 4: Retrieving Stored Hints ===")
    
    headers = {
        "Authorization": f"Bearer {BACKEND_API_KEY}"
    }
    
    # Get all hints
    response = requests.get(
        f"{BACKEND_URL}/regions/{TEST_REGION['vnum']}/hints",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retrieved {data['total_count']} hints")
        print(f"   Active: {data['active_count']}")
        print(f"   Categories: {json.dumps(data['categories'], indent=2)}")
        
        # Test filtering by category
        for category in ["atmosphere", "flora", "fauna"]:
            response = requests.get(
                f"{BACKEND_URL}/regions/{TEST_REGION['vnum']}/hints",
                headers=headers,
                params={"category": category}
            )
            if response.status_code == 200:
                cat_data = response.json()
                print(f"   {category}: {cat_data['total_count']} hints")
    else:
        print(f"❌ Failed to retrieve hints: {response.status_code}")
        return False
    
    # Get profile
    response = requests.get(
        f"{BACKEND_URL}/regions/{TEST_REGION['vnum']}/profile",
        headers=headers
    )
    
    if response.status_code == 200:
        profile = response.json()
        print(f"\n✅ Retrieved region profile:")
        print(f"   Theme: {profile['overall_theme'][:100]}...")
        print(f"   Mood: {profile['dominant_mood']}")
        print(f"   Style: {profile['description_style']}")
    else:
        print(f"⚠️ No profile found for region")
    
    return True


def test_analytics():
    """Step 5: Test analytics endpoint"""
    print("\n=== Step 5: Testing Analytics ===")
    
    headers = {
        "Authorization": f"Bearer {BACKEND_API_KEY}"
    }
    
    response = requests.get(
        f"{BACKEND_URL}/regions/{TEST_REGION['vnum']}/hints/analytics",
        headers=headers
    )
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"✅ Analytics retrieved:")
        print(f"   Total hints: {analytics['total_hints']}")
        print(f"   Active hints: {analytics['active_hints']}")
        print(f"   Average priority: {analytics['average_priority']:.2f}")
        print(f"   Profile exists: {analytics['profile_exists']}")
        
        if analytics['category_distribution']:
            print(f"   Distribution: {json.dumps(analytics['category_distribution'], indent=2)}")
    else:
        print(f"❌ Failed to get analytics: {response.status_code}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("REGION HINTS SYSTEM TEST")
    print("=" * 60)
    print(f"\nTesting with region: {TEST_REGION['name']} (VNUM: {TEST_REGION['vnum']})")
    
    # Check services
    print("\n=== Checking Service Availability ===")
    
    # Check backend
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend API is running")
        else:
            print(f"⚠️ Backend API returned: {response.status_code}")
    except:
        print("❌ Backend API is not accessible at", BACKEND_URL)
        print("   Please start the backend: cd apps/backend/src && python -m uvicorn main:app --reload")
        return
    
    # Check MCP
    try:
        response = requests.get(f"{MCP_URL}/status", headers={"X-API-Key": MCP_API_KEY})
        if response.status_code == 200:
            status = response.json()
            print(f"✅ MCP Server is running (v{status['mcp_server']['version']})")
            print(f"   Available tools: {status['mcp_server']['capabilities']['tools']}")
        else:
            print(f"⚠️ MCP Server returned: {response.status_code}")
    except:
        print("❌ MCP Server is not accessible at", MCP_URL)
        print("   Please start the MCP server: cd apps/mcp && python run_dev.py")
        return
    
    # Run tests
    success = True
    
    # Step 1: Create region
    if not test_create_region():
        print("\n❌ Failed to create test region")
        success = False
    
    # Step 2: Generate hints
    hints_data = test_generate_hints()
    if not hints_data:
        print("\n❌ Failed to generate hints")
        success = False
    
    # Step 3: Store hints
    if hints_data and not test_store_hints(hints_data):
        print("\n❌ Failed to store hints")
        success = False
    
    # Step 4: Retrieve hints
    if not test_retrieve_hints():
        print("\n❌ Failed to retrieve hints")
        success = False
    
    # Step 5: Analytics
    if not test_analytics():
        print("\n⚠️ Analytics test failed (non-critical)")
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ REGION HINTS SYSTEM TEST COMPLETED SUCCESSFULLY")
        print(f"\nThe Crystal Caverns (VNUM: {TEST_REGION['vnum']}) is ready with hints!")
        print("\nYou can now:")
        print("1. View hints at: http://localhost:8000/docs")
        print("2. Use the region in the game's dynamic description engine")
        print("3. Test different weather/time conditions for varied descriptions")
    else:
        print("❌ REGION HINTS SYSTEM TEST FAILED")
        print("\nPlease check the error messages above and ensure:")
        print("1. Backend is running on port 8000")
        print("2. MCP server is running on port 8001")
        print("3. Database has the region_hints tables")
        print("4. API keys are correctly configured")
    print("=" * 60)


if __name__ == "__main__":
    main()
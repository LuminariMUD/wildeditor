#!/usr/bin/env python3
"""Test script to validate the new region_props functionality"""

import sys
import os

# Add the backend src directory to the Python path
backend_src = os.path.join(os.path.dirname(__file__), 'apps', 'backend', 'src')
sys.path.insert(0, backend_src)

from schemas.region import RegionCreate
from pydantic import ValidationError

def test_region_validation():
    """Test the new region_props validation logic"""
    
    print("Testing Region Properties Validation")
    print("=" * 50)
    
    # Test 1: Geographic region with any value (should pass)
    try:
        region = RegionCreate(
            vnum=1001,
            zone_vnum=1,
            name="Test Geographic",
            region_type=1,  # Geographic
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="0"
        )
        print("✓ Geographic region with props='0': PASSED")
    except ValidationError as e:
        print(f"✗ Geographic region validation failed: {e}")
    
    # Test 2: Encounter region with mob vnums (should pass)
    try:
        region = RegionCreate(
            vnum=1002,
            zone_vnum=1,
            name="Test Encounter Zone",
            region_type=2,  # Encounter
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="1001,1002,1003"
        )
        print("✓ Encounter region with mob vnums='1001,1002,1003': PASSED")
    except ValidationError as e:
        print(f"✗ Encounter region validation failed: {e}")
    
    # Test 3: Encounter region with single mob vnum (should pass)
    try:
        region = RegionCreate(
            vnum=1003,
            zone_vnum=1,
            name="Test Single Mob",
            region_type=2,  # Encounter
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="5001"
        )
        print("✓ Encounter region with single mob vnum='5001': PASSED")
    except ValidationError as e:
        print(f"✗ Single mob vnum validation failed: {e}")
    
    # Test 4: Encounter region with "0" (no encounters) (should pass)
    try:
        region = RegionCreate(
            vnum=1004,
            zone_vnum=1,
            name="Test No Encounters",
            region_type=2,  # Encounter
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="0"
        )
        print("✓ Encounter region with no encounters='0': PASSED")
    except ValidationError as e:
        print(f"✗ No encounters validation failed: {e}")
    
    # Test 5: Transform region with elevation adjustment (should pass)
    try:
        region = RegionCreate(
            vnum=1005,
            zone_vnum=1,
            name="Test Elevation Raise",
            region_type=3,  # Transform
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="50"
        )
        print("✓ Transform region with elevation='+50': PASSED")
    except ValidationError as e:
        print(f"✗ Transform elevation validation failed: {e}")
    
    # Test 6: Transform region with negative elevation (should pass)
    try:
        region = RegionCreate(
            vnum=1006,
            zone_vnum=1,
            name="Test Elevation Lower",
            region_type=3,  # Transform
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="-30"
        )
        print("✓ Transform region with elevation='-30': PASSED")
    except ValidationError as e:
        print(f"✗ Negative elevation validation failed: {e}")
    
    # Test 7: Sector override with valid sector (should pass)
    try:
        region = RegionCreate(
            vnum=1007,
            zone_vnum=1,
            name="Test Road Override",
            region_type=4,  # Sector Override
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="11"  # Road North-South
        )
        print("✓ Sector override with valid sector='11' (Road): PASSED")
    except ValidationError as e:
        print(f"✗ Sector override validation failed: {e}")
    
    # Test 8: Sector override with invalid sector (should fail)
    try:
        region = RegionCreate(
            vnum=1008,
            zone_vnum=1,
            name="Test Invalid Sector",
            region_type=4,  # Sector Override
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="99"  # Invalid sector
        )
        print("✗ Sector override with invalid sector='99': SHOULD HAVE FAILED!")
    except ValidationError as e:
        print("✓ Sector override with invalid sector='99': CORRECTLY FAILED")
    
    # Test 9: Encounter with invalid mob vnum format (should fail)
    try:
        region = RegionCreate(
            vnum=1009,
            zone_vnum=1,
            name="Test Invalid Mob Format",
            region_type=2,  # Encounter
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props="abc,def"  # Invalid format
        )
        print("✗ Encounter with invalid format 'abc,def': SHOULD HAVE FAILED!")
    except ValidationError as e:
        print("✓ Encounter with invalid format 'abc,def': CORRECTLY FAILED")
    
    print("\nValidation tests completed!")

if __name__ == "__main__":
    test_region_validation()

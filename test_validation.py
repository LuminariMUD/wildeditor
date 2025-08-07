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
            region_props=0  # Integer value ignored by game
        )
        print("✓ Geographic region with props=0: PASSED")
    except ValidationError as e:
        print(f"✗ Geographic region validation failed: {e}")
    
    # Test 2: Encounter region with mob vnums in region_reset_data (should pass)
    try:
        region = RegionCreate(
            vnum=1002,
            zone_vnum=1,
            name="Test Encounter Zone",
            region_type=2,  # Encounter
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props=0,  # Integer value ignored by game
            region_reset_data="1001,1002,1003"  # Mob vnums go here
        )
        print("✓ Encounter region with mob vnums in region_reset_data='1001,1002,1003': PASSED")
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
            region_props=0,
            region_reset_data="5001"  # Single mob vnum
        )
        print("✓ Encounter region with single mob vnum in region_reset_data='5001': PASSED")
    except ValidationError as e:
        print(f"✗ Single mob vnum validation failed: {e}")
    
    # Test 4: Encounter region with empty reset data (no encounters) (should pass)
    try:
        region = RegionCreate(
            vnum=1004,
            zone_vnum=1,
            name="Test No Encounters",
            region_type=2,  # Encounter
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props=0,
            region_reset_data=""  # Empty for no encounters
        )
        print("✓ Encounter region with no encounters (empty region_reset_data): PASSED")
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
            region_props=50  # Positive elevation adjustment
        )
        print("✓ Transform region with elevation=50: PASSED")
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
            region_props=-30  # Negative elevation adjustment
        )
        print("✓ Transform region with elevation=-30: PASSED")
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
            region_props=11  # Road North-South
        )
        print("✓ Sector override with valid sector=11 (Road): PASSED")
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
            region_props=99  # Invalid sector
        )
        print("✗ Sector override with invalid sector=99: SHOULD HAVE FAILED!")
    except ValidationError as e:
        print("✓ Sector override with invalid sector=99: CORRECTLY FAILED")
    
    # Test 9: Encounter with invalid mob vnum format in region_reset_data (should fail)
    try:
        region = RegionCreate(
            vnum=1009,
            zone_vnum=1,
            name="Test Invalid Mob Format",
            region_type=2,  # Encounter
            coordinates=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
            region_props=0,
            region_reset_data="abc,def"  # Invalid format
        )
        print("✗ Encounter with invalid format 'abc,def' in region_reset_data: SHOULD HAVE FAILED!")
    except ValidationError as e:
        print("✓ Encounter with invalid format 'abc,def' in region_reset_data: CORRECTLY FAILED")
    
    print("\nValidation tests completed!")

if __name__ == "__main__":
    test_region_validation()

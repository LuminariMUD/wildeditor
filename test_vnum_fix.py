#!/usr/bin/env python3
import sys
import os
backend_src = os.path.join(os.path.dirname(__file__), 'apps', 'backend', 'src')
sys.path.insert(0, backend_src)

from schemas.region import RegionResponse

# Test with the actual data that was failing
data = {
    'vnum': 1000001,
    'zone_vnum': 10000,
    'name': 'Test Encounter',
    'region_type': 2,
    'coordinates': [],
    'region_props': 0,
    'region_reset_data': '1000126,1000127,1000128,1000129',
    'region_reset_time': None
}

try:
    region = RegionResponse(**data)
    print('✓ Validation passed for encounter with mob vnums:', region.region_reset_data)
except Exception as e:
    print('✗ Validation failed:', e)

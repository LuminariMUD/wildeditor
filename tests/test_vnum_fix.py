#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "backend" / "src"))

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

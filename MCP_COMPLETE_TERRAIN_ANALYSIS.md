# Enhanced MCP Wilderness Map with Region/Path Overlays

## 🔍 **Critical Issue Identified**

The current MCP wilderness map generation is **incomplete** because it only shows base terrain data from the game engine, but **missing region and path overlays** that can significantly modify:

- **Sector types** (e.g., road paths override forest with road sector)
- **Elevation** (e.g., valley regions lower elevation, bridge paths raise it)
- **Temperature/Moisture** (e.g., river paths add moisture)
- **Movement properties** (e.g., roads speed travel, swamps slow it)
- **Spawn locations** (e.g., encounter regions add monster spawns)
- **Geographic names** (e.g., "Darkwood Forest" vs generic "forest")

## 🎯 **Required Enhancement**

The MCP map generation needs to be enhanced to provide **complete terrain data** including:

### **1. Base Terrain Data** ✅ (Already working)
- Elevation, temperature, moisture from game engine
- Base sector types from terrain bridge

### **2. Region Overlays** ❌ (Missing)
- **Geographic regions** (type 1): Names and contextual info
- **Encounter regions** (type 2): Spawn zones and special encounters  
- **Transform regions** (type 3): Elevation/drainage modifications
- **Sector regions** (type 4): Complete terrain overrides

### **3. Path Overlays** ❌ (Missing)
- **Roads** (types 1-2): Movement bonuses, sector overrides
- **Rivers/Streams** (types 3-4): Water movement, moisture effects
- **Trails** (type 5): Path navigation bonuses
- **Bridges/Tunnels** (types 6-7): Special crossing mechanics

## 🔧 **Implementation Strategy**

### **Option A: Backend Enhancement** (Recommended)
Create new backend endpoint: `GET /api/terrain/complete-map-data`

```python
@router.get("/complete-map-data")
async def get_complete_terrain_data(
    center_x: int, center_y: int, radius: int,
    include_regions: bool = True,
    include_paths: bool = True
):
    """
    Get complete terrain data including base terrain + region/path overlays
    """
    # 1. Get base terrain data (existing)
    base_terrain = await get_terrain_batch(...)
    
    # 2. Get regions affecting each coordinate
    regions_data = await get_regions_at_coordinates(coordinate_list)
    
    # 3. Get paths affecting each coordinate  
    paths_data = await get_paths_at_coordinates(coordinate_list)
    
    # 4. Merge and apply overlays in priority order
    complete_data = merge_terrain_overlays(base_terrain, regions_data, paths_data)
    
    return complete_data
```

### **Option B: MCP Enhancement** (Current approach)
Enhance MCP to make multiple backend calls and merge data:

1. Call existing `/terrain/map-data` for base terrain
2. Call `/regions` to get all regions, filter by area
3. Call `/paths` to get all paths, filter by area  
4. Apply spatial intersection logic in MCP
5. Merge overlays in proper priority order

## 🚀 **Enhanced MCP Tool**

```python
async def _generate_complete_wilderness_map(self, center_x: int, center_y: int, radius: int = 10):
    """Generate complete wilderness map with all overlays"""
    
    # 1. Get base terrain
    base_terrain = await self._get_base_terrain_map(center_x, center_y, radius)
    
    # 2. Get regions affecting this area
    regions = await self._get_regions_in_area(center_x, center_y, radius)
    
    # 3. Get paths affecting this area
    paths = await self._get_paths_in_area(center_x, center_y, radius)
    
    # 4. Apply overlays to each coordinate
    enhanced_map = {}
    for coord_key, terrain in base_terrain.items():
        enhanced_map[coord_key] = self._apply_terrain_overlays(
            terrain, regions, paths
        )
    
    return {
        "center": {"x": center_x, "y": center_y},
        "radius": radius,
        "map_data": enhanced_map,
        "overlays": {
            "regions_count": len(regions),
            "paths_count": len(paths),
            "affected_coordinates": len([c for c in enhanced_map.values() if c.get('overlays')])
        },
        "source": "complete_terrain_analysis"
    }

def _apply_terrain_overlays(self, base_terrain, regions, paths):
    """Apply region and path overlays to base terrain"""
    result = base_terrain.copy()
    result['overlays'] = {
        'regions': [],
        'paths': [],
        'modifications': []
    }
    
    # Apply regions in priority order (1-4)
    for region in sorted(regions, key=lambda r: r['type']):
        if self._point_in_region(base_terrain['x'], base_terrain['y'], region):
            result['overlays']['regions'].append(region['name'])
            
            if region['type'] == 1:  # Geographic naming
                result['geographic_name'] = region['name']
            elif region['type'] == 2:  # Encounter zone
                result['encounter_zone'] = region['name']
                result['spawn_info'] = region.get('props', {})
            elif region['type'] == 3:  # Transform elevation
                result['elevation'] = self._apply_elevation_transform(
                    result['elevation'], region
                )
                result['overlays']['modifications'].append(f"Elevation modified by {region['name']}")
            elif region['type'] == 4:  # Sector override
                result['sector_type'] = region['sector_override']
                result['sector_name'] = region['sector_name']
                result['overlays']['modifications'].append(f"Sector overridden by {region['name']}")
    
    # Apply paths (processed after regions)
    for path in paths:
        if self._point_on_path(base_terrain['x'], base_terrain['y'], path):
            result['overlays']['paths'].append(path['name'])
            
            # Path sector mappings
            path_sectors = {
                1: 17,  # Road
                2: 18,  # Dirt Road  
                3: 7,   # River (Water)
                4: 34,  # Stream
                5: 2    # Trail (Field)
            }
            
            if path['type'] in path_sectors:
                result['sector_type'] = path_sectors[path['type']]
                result['overlays']['modifications'].append(f"Path sector from {path['name']}")
            
            # Environmental effects
            if path['type'] in [3, 4]:  # Rivers/streams
                result['moisture'] = min(255, result['moisture'] + 20)
                result['overlays']['modifications'].append(f"Moisture increased by {path['name']}")
    
    return result
```

## 📊 **Expected Enhanced Output**

Instead of basic terrain data:
```json
{
  "0,0": {
    "x": 0, "y": 0,
    "elevation": 170,
    "sector_type": 3,
    "sector_name": "Forest"
  }
}
```

Complete enhanced data:
```json
{
  "0,0": {
    "x": 0, "y": 0,
    "elevation": 170,
    "sector_type": 17,
    "sector_name": "Road",
    "temperature": 24,
    "moisture": 127,
    "geographic_name": "Darkwood Forest",
    "overlays": {
      "regions": ["Darkwood Forest"],
      "paths": ["Great Trade Road"],
      "modifications": [
        "Named by Darkwood Forest",
        "Path sector from Great Trade Road"
      ]
    },
    "movement_bonus": 1.5,
    "path_info": {
      "type": "road",
      "width": "wide",
      "condition": "well-maintained"
    }
  }
}
```

## 🎯 **Immediate Action Needed**

This enhancement is **critical for AI agents** creating regions and paths because they need to:

1. **See existing overlays** to avoid conflicts
2. **Understand terrain interactions** between regions/paths
3. **Make informed decisions** about placement
4. **Validate against real terrain state** not just base terrain

Without this data, the MCP is providing **incomplete and potentially misleading** terrain information for wilderness management decisions.

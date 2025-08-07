from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Union
from datetime import datetime

# Region type constants
REGION_GEOGRAPHIC = 1      # Named areas
REGION_ENCOUNTER = 2       # Encounter zones  
REGION_SECTOR_TRANSFORM = 3 # Terrain modification (elevation adjustment)
REGION_SECTOR = 4          # Complete terrain override

# Sector type constants for REGION_SECTOR (complete LuminariMUD sector types)
SECTOR_TYPES = {
    0: "Inside", 1: "City", 2: "Field", 3: "Forest", 4: "Hills", 5: "Low Mountains",
    6: "Water (Swim)", 7: "Water (No Swim)", 8: "In Flight", 9: "Underwater", 10: "Zone Entrance",
    11: "Road North-South", 12: "Road East-West", 13: "Road Intersection", 14: "Desert", 15: "Ocean",
    16: "Marshland", 17: "High Mountains", 18: "Outer Planes", 19: "Underdark - Wild", 20: "Underdark - City",
    21: "Underdark - Inside", 22: "Underdark - Water (Swim)", 23: "Underdark - Water (No Swim)", 24: "Underdark - In Flight",
    25: "Lava", 26: "Dirt Road North-South", 27: "Dirt Road East-West", 28: "Dirt Road Intersection", 29: "Cave",
    30: "Jungle", 31: "Tundra", 32: "Taiga", 33: "Beach", 34: "Sea Port", 35: "Inside Room", 36: "River"
}

class RegionBase(BaseModel):
    vnum: int
    zone_vnum: int
    name: str  # Required in API even though nullable in DB
    region_type: int
    coordinates: Optional[List[Dict[str, float]]] = []  # Optional since region_polygon is nullable in DB
    region_props: Optional[int] = 0  # Integer for sector types and elevation adjustments
    region_reset_data: str = ""  # For encounter mob vnums and other reset data
    region_reset_time: Optional[datetime] = None  # Optional to handle MySQL zero dates gracefully
    
    @validator('name')
    def validate_name_required(cls, v):
        if not v or not v.strip():
            raise ValueError('Name is required and cannot be empty')
        if len(v) > 50:
            raise ValueError('Name cannot be longer than 50 characters')
        return v.strip()
    
    @validator('region_type')
    def validate_region_type(cls, v):
        if v not in [REGION_GEOGRAPHIC, REGION_ENCOUNTER, REGION_SECTOR_TRANSFORM, REGION_SECTOR]:
            raise ValueError(f'Region type must be one of: {REGION_GEOGRAPHIC} (Geographic), {REGION_ENCOUNTER} (Encounter), {REGION_SECTOR_TRANSFORM} (Sector Transform), {REGION_SECTOR} (Sector Override)')
        return v
    
    @validator('region_props')
    def validate_region_props(cls, v, values):
        if 'region_type' in values:
            region_type = values['region_type']
            
            # REGION_GEOGRAPHIC: region_props ignored by game, can be any integer
            if region_type == REGION_GEOGRAPHIC:
                return v if v is not None else 0
            
            # REGION_ENCOUNTER: region_props ignored by game, mob vnums go in region_reset_data
            if region_type == REGION_ENCOUNTER:
                return v if v is not None else 0
                
            # REGION_SECTOR_TRANSFORM: elevation adjustment value (integer)
            if region_type == REGION_SECTOR_TRANSFORM:
                if v is None:
                    return 0
                # Allow any integer value (positive or negative elevation adjustment)
                return int(v)
                
            # REGION_SECTOR: must be valid sector type (0-36)
            if region_type == REGION_SECTOR:
                if v is None:
                    return 0
                if v not in SECTOR_TYPES:
                    valid_sectors = ', '.join(f'{k}: {v}' for k, v in list(SECTOR_TYPES.items())[:10])
                    raise ValueError(f'Invalid sector type for REGION_SECTOR. Valid values (0-36): {valid_sectors}...')
                return v
        
        # Default to 0 if no validation applies
        return v if v is not None else 0
    
    @validator('region_reset_data')
    def validate_region_reset_data(cls, v, values):
        if 'region_type' in values:
            region_type = values['region_type']
            
            # REGION_ENCOUNTER: validate mob vnums in region_reset_data
            if region_type == REGION_ENCOUNTER:
                if not v or v.strip() == "":
                    return ""  # Allow empty for no encounters
                
                # Check if it's a comma-separated list of integers (mob vnums)
                try:
                    mob_vnums = [int(x.strip()) for x in v.split(',') if x.strip()]
                    if not mob_vnums:
                        return ""  # Empty list defaults to empty string
                    
                    # Validate vnum ranges (LuminariMUD vnum range)
                    for vnum in mob_vnums:
                        if vnum < 1 or vnum > 99999999:
                            raise ValueError(f'Invalid mob vnum: {vnum}. Must be between 1 and 99999999.')
                    
                    return ','.join(str(vnum) for vnum in mob_vnums)
                except ValueError as e:
                    if "invalid literal" in str(e):
                        raise ValueError('REGION_ENCOUNTER region_reset_data must be comma-separated mob vnums (e.g., "1001,1002,1003") or empty for no encounters')
                    raise e
        
        # For non-encounter regions, allow any string
        return v if v is not None else ""
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        # Allow empty or None coordinates (regions without polygon data)
        if not v:
            return []  # Return empty list for consistency
        
        # Allow any number of coordinates - database contains valid spatial data
        # Single points = landmarks, 2+ points = polygons/areas, duplicates are valid for small areas
        for i, coord in enumerate(v):
            if 'x' not in coord or 'y' not in coord:
                raise ValueError(f'Coordinate {i} must have x and y values')
            
            # Ensure coordinates are numeric
            try:
                float(coord['x'])
                float(coord['y'])
            except (ValueError, TypeError):
                raise ValueError(f'Coordinate {i} x and y values must be numeric')
        
        return v

class RegionCreate(RegionBase):
    pass

class RegionUpdate(BaseModel):
    vnum: Optional[int] = None
    zone_vnum: Optional[int] = None
    name: Optional[str] = None
    region_type: Optional[int] = None
    coordinates: Optional[List[Dict[str, float]]] = None
    region_props: Optional[str] = None
    region_reset_data: Optional[str] = None
    region_reset_time: Optional[datetime] = None
    
    @validator('name')
    def validate_name_if_provided(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Name cannot be empty')
            if len(v) > 50:
                raise ValueError('Name cannot be longer than 50 characters')
            return v.strip()
        return v

class RegionResponse(RegionBase):
    # Add human-readable type and sector descriptions
    region_type_name: Optional[str] = None
    sector_type_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Helper function to create a landmark/point region (as geographic type)
def create_landmark_region(x: float, y: float, name: str, vnum: int, zone_vnum: int, radius: float = 0.2) -> dict:
    """
    Create a small square polygon around a point coordinate for landmarks/POIs.
    
    Landmarks are single-point geographic regions used by the dynamic description 
    engine to provide contextual references for wilderness room descriptions.
    Examples include city gates, notable buildings, geographical markers, and
    other points of interest that enhance the immersive experience.
    
    These are created as 'geographic' type regions that don't modify terrain
    but provide location context for description generation.
    """
    return {
        "vnum": vnum,
        "zone_vnum": zone_vnum,
        "name": name,
        "region_type": REGION_GEOGRAPHIC,
        "coordinates": [
            {"x": x - radius, "y": y - radius},
            {"x": x - radius, "y": y + radius},
            {"x": x + radius, "y": y + radius},
            {"x": x + radius, "y": y - radius},
            {"x": x - radius, "y": y - radius}  # Close the polygon
        ],
        "region_props": None,  # Not used for geographic regions
        "region_reset_data": "",
        "region_reset_time": datetime.now()
    }

def get_region_type_name(region_type: int) -> str:
    """Get human-readable name for region type"""
    type_names = {
        REGION_GEOGRAPHIC: "Geographic",
        REGION_ENCOUNTER: "Encounter", 
        REGION_SECTOR_TRANSFORM: "Sector Transform",
        REGION_SECTOR: "Sector Override"
    }
    return type_names.get(region_type, f"Unknown ({region_type})")

def get_sector_type_name(sector_id: int) -> str:
    """Get human-readable name for sector type"""
    return SECTOR_TYPES.get(sector_id, f"Unknown ({sector_id})")

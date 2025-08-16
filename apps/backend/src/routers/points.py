from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from ..models.region import Region
from ..models.path import Path
from ..schemas.region import get_region_type_name, get_sector_type_name, REGION_SECTOR
from ..config.config_database import get_db

router = APIRouter()

@router.get("", response_model=dict)
@router.get("/", response_model=dict)
def get_point_info(
    x: float = Query(..., description="X coordinate"), 
    y: float = Query(..., description="Y coordinate"),
    radius: Optional[float] = Query(0.1, description="Search radius around the point"),
    db: Session = Depends(get_db)
):
    """
    Get information about what regions and paths exist at or near a specific coordinate point.
    This is useful for finding what's at a specific location on the map.
    """
    try:
        # Create a point geometry for spatial queries
        point_wkt = f"POINT({x} {y})"
        
        # Find regions that contain this point or are within radius
        regions_query = text("""
            SELECT vnum, zone_vnum, name, region_type, region_props, region_reset_data, region_reset_time,
                   ST_AsText(region_polygon) as polygon_wkt
            FROM region_data 
            WHERE region_polygon IS NOT NULL 
            AND (ST_Contains(region_polygon, ST_GeomFromText(:point)) 
                 OR ST_Distance(region_polygon, ST_GeomFromText(:point)) <= :radius)
        """)
        
        region_results = db.execute(regions_query, {
            "point": point_wkt, 
            "radius": radius
        }).fetchall()
        
        matching_regions = []
        for row in region_results:
            region_info = {
                "vnum": row.vnum,
                "zone_vnum": row.zone_vnum,
                "name": row.name,
                "region_type": row.region_type,
                "region_type_name": get_region_type_name(row.region_type),
                "region_props": row.region_props,
                "sector_type_name": get_sector_type_name(row.region_props) if row.region_type == REGION_SECTOR and row.region_props else None,
                "region_reset_data": row.region_reset_data,
                "region_reset_time": row.region_reset_time
            }
            matching_regions.append(region_info)
        
        # Find paths that pass through or near this point using spatial queries
        paths_query = text("""
            SELECT pd.vnum, pd.zone_vnum, pd.name, pd.path_type, pd.path_props,
                   ST_AsText(pd.path_linestring) as linestring_wkt
            FROM path_data pd 
            WHERE pd.path_linestring IS NOT NULL 
            AND (ST_Distance(pd.path_linestring, ST_GeomFromText(:point)) <= :radius)
        """)
        
        path_results = db.execute(paths_query, {
            "point": point_wkt,
            "radius": radius
        }).fetchall()
        
        matching_paths = []
        for row in path_results:
            path_info = {
                "vnum": row.vnum,
                "zone_vnum": row.zone_vnum,
                "name": row.name,
                "path_type": row.path_type,
                "path_type_name": _get_path_type_name(row.path_type),
                "path_props": row.path_props
            }
            matching_paths.append(path_info)
        
        return {
            "coordinate": {"x": x, "y": y},
            "radius": radius,
            "regions": matching_regions,
            "paths": matching_paths,
            "summary": {
                "region_count": len(matching_regions),
                "path_count": len(matching_paths)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving point information: {str(e)}"
        )

def _get_path_type_name(path_type: int) -> str:
    """
    Convert path type number to human-readable name.
    """
    path_type_names = {
        0: "Road",
        1: "Paved Road", 
        2: "Dirt Road",
        3: "Geographic",
        4: "River",
        5: "River",  # Both 4 and 5 are rivers in the current data
        6: "Trail"
    }
    return path_type_names.get(path_type, f"Unknown Type {path_type}")

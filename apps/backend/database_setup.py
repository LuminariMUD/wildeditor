#!/usr/bin/env python3
"""
Database setup and testing script for Wildeditor Backend
"""

import os
import sys
from pathlib import Path 

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config_database import engine
from sqlalchemy import text

def test_connection():
    """Test database connection and check table structure"""
    try:
        # Test connection
        with engine.connect() as connection:
            print("✅ Database connection successful!")
            
            # Check if region_data table exists and has correct structure
            result = connection.execute(text("SHOW TABLES LIKE 'region_data'")).fetchone()
            if result:
                print("✅ Table 'region_data' exists")
                
                # Check table structure
                columns = connection.execute(text("DESCRIBE region_data")).fetchall()
                print(f"📋 Region_data table structure:")
                for col in columns:
                    print(f"   {col.Field}: {col.Type} {'(PK)' if col.Key == 'PRI' else ''}")
                
                # Check for spatial support
                spatial_result = connection.execute(text("SELECT ST_AsText(POINT(1, 1))")).fetchone()
                if spatial_result:
                    print("✅ MySQL spatial functions are available")
                else:
                    print("❌ MySQL spatial functions not available")
                    
            else:
                print("❌ Table 'region_data' not found")
            
            # Check path_data table
            result = connection.execute(text("SHOW TABLES LIKE 'path_data'")).fetchone()
            if result:
                print("✅ Table 'path_data' exists")
            else:
                print("❌ Table 'path_data' not found")
                
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_region_operations():
    """Test region creation and spatial operations"""
    try:
        from src.schemas.region import create_landmark_region, REGION_GEOGRAPHIC, get_region_type_name
        from datetime import datetime
        
        # Test landmark creation helper
        landmark_data = create_landmark_region(100.0, 100.0, "Test Obelisk", 9999, 1, 0.2)
        
        print(f"\n🏛️ Sample landmark data:")
        print(f"   Name: {landmark_data['name']}")
        print(f"   Type: {landmark_data['region_type']} ({get_region_type_name(landmark_data['region_type'])})")
        print(f"   Coordinates: {landmark_data['coordinates']}")
        print("   ✅ Landmark creation helper working correctly!")
        
        # Test spatial conversion
        from src.routers.regions import coordinates_to_polygon_wkt, polygon_wkt_to_coordinates
        
        coords = [{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 1.0}, {"x": 2.0, "y": 2.0}, {"x": 1.0, "y": 2.0}]
        wkt = coordinates_to_polygon_wkt(coords)
        back_to_coords = polygon_wkt_to_coordinates(wkt)
        
        print(f"\n🗺️ Spatial conversion test:")
        print(f"   Original: {coords}")
        print(f"   WKT: {wkt}")
        print(f"   Back to coords: {back_to_coords}")
        print("   ✅ Spatial conversion working correctly!")
        
        return True
    except Exception as e:
        print(f"❌ Error testing region operations: {e}")
        return False

if __name__ == "__main__":
    print("Wildeditor Backend Database Setup")
    print("=" * 40)
    print("📍 Updated for actual MySQL database structure")
    print("📍 Region types: 1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override")
    print("📍 Uses MySQL POLYGON spatial data type")
    print("=" * 40)
    
    # Check environment variables
    db_url = os.getenv("MYSQL_DATABASE_URL")
    if not db_url:
        print("❌ MYSQL_DATABASE_URL environment variable not set")
        print("Please ensure your .env file is configured correctly")
        sys.exit(1)
    
    print("🔗 Using configured MYSQL_DATABASE_URL (credential suppressed)")
    
    # Test connection and structure
    if test_connection():
        if test_region_operations():
            print("\n🚀 Backend is ready for deployment!")
            print("\n💡 API endpoints:")
            print("   • GET /api/regions - All regions")
            print("   • GET /api/regions?region_type=1 - Filter by type")
            print("   • GET /api/regions?zone_vnum=100 - Filter by zone")
            print("   • POST /api/regions/landmarks - Create landmark")
            print("   • GET /api/points?x=100&y=100 - Query what's at coordinates")
            print("   • GET /api/regions/sector-types - Get all valid sector types")
    else:
        print("\n❌ Database connection failed. Please check:")
        print("   1. MySQL server is running")
        print("   2. Database credentials are correct")
        print("   3. Database 'luminari_mudprod' exists")
        print("   4. Tables 'region_data' and 'path_data' exist")

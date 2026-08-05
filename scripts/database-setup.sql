-- Luminari Wilderness Editor Database Setup
-- 
-- MySQL Database Schema for Development and Production
-- This matches the actual table structure used by the FastAPI backend
--
-- USAGE:
--   For Development: Replace 'luminari_wilderness' with 'luminari_muddev'
--   For Production:  Replace 'luminari_wilderness' with 'luminari_mudprod'
--   Or set the database name via environment variable before running

-- Create the database if it doesn't exist
-- DEVELOPMENT: CREATE DATABASE IF NOT EXISTS luminari_muddev;
-- PRODUCTION:  CREATE DATABASE IF NOT EXISTS luminari_mudprod;
CREATE DATABASE IF NOT EXISTS luminari_wilderness;
USE luminari_wilderness;

-- Create region_data table (matches backend Region model)
CREATE TABLE IF NOT EXISTS region_data (
  vnum INT(11) PRIMARY KEY,                    -- Primary key, not auto-increment (managed by game)
  zone_vnum INT(11) NOT NULL,                  -- Zone this region belongs to
  name VARCHAR(50),                            -- Region name (nullable in real DB)
  region_type INT(11) NOT NULL,                -- 1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override
  region_polygon POLYGON,                      -- MySQL spatial polygon type (nullable)
  region_props INT(11),                        -- Usage depends on region_type (nullable)
  region_reset_data VARCHAR(255) NOT NULL,     -- Reset data string
  region_reset_time DATETIME NOT NULL         -- Reset time
) ENGINE=InnoDB;

-- Create path_data table (matches backend Path model)
CREATE TABLE IF NOT EXISTS path_data (
  vnum INT(11) PRIMARY KEY,                    -- Primary key, not auto-increment (managed by game)
  zone_vnum INT(11) NOT NULL DEFAULT 10000,   -- Zone this path belongs to (default zone)
  path_type INT(11) NOT NULL,                  -- Path type (roads, rivers, etc.)
  name VARCHAR(50) NOT NULL,                   -- Path name (50 char limit from real DB)
  path_props INT(11),                          -- Additional properties (nullable)
  path_linestring LINESTRING                  -- MySQL spatial linestring (nullable)
) ENGINE=InnoDB;

-- Note: Points table is not used in production - points are queried spatially from regions/paths

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_region_data_vnum ON region_data(vnum);
CREATE INDEX IF NOT EXISTS idx_region_data_zone_vnum ON region_data(zone_vnum);
CREATE INDEX IF NOT EXISTS idx_region_data_type ON region_data(region_type);
CREATE SPATIAL INDEX IF NOT EXISTS idx_region_polygon ON region_data(region_polygon);

CREATE INDEX IF NOT EXISTS idx_path_data_vnum ON path_data(vnum);
CREATE INDEX IF NOT EXISTS idx_path_data_zone_vnum ON path_data(zone_vnum);
CREATE INDEX IF NOT EXISTS idx_path_data_type ON path_data(path_type);
CREATE SPATIAL INDEX IF NOT EXISTS idx_path_linestring ON path_data(path_linestring);

-- Create database user for the wildeditor backend
-- Run these commands separately as a MySQL admin user:
--

-- FOR DEVELOPMENT:
-- CREATE USER 'wildeditor_user'@'%' IDENTIFIED BY 'your_dev_password';
-- GRANT ALL PRIVILEGES ON luminari_muddev.* TO 'wildeditor_user'@'%';
-- FLUSH PRIVILEGES;
--
-- FOR PRODUCTION:
-- CREATE USER 'wildeditor_user'@'%' IDENTIFIED BY 'your_secure_prod_password';
-- GRANT ALL PRIVILEGES ON luminari_mudprod.* TO 'wildeditor_user'@'%';
-- FLUSH PRIVILEGES;

-- Sample data for testing (optional) - COMMENTED OUT
-- Uncomment these if you need sample data for testing

-- Geographic region (forest area)
-- INSERT IGNORE INTO region_data (vnum, zone_vnum, name, region_type, region_polygon, region_props, region_reset_data, region_reset_time) 
-- VALUES (
--   1001, 
--   100, 
--   'Darkwood Forest', 
--   1, 
--   ST_GeomFromText('POLYGON((100 100, 200 100, 200 200, 100 200, 100 100))'), 
--   3, 
--   'reset_data', 
--   NOW()
-- );

-- Sample path (forest road)
-- INSERT IGNORE INTO path_data (vnum, zone_vnum, path_type, name, path_props, path_linestring) 
-- VALUES (
--   2001, 
--   100, 
--   1, 
--   'Forest Road', 
--   0, 
--   ST_GeomFromText('LINESTRING(100 150, 200 150)')
-- );

-- Verify spatial functions are working
SELECT 
  'Spatial functions test' as test_name,
  ST_AsText(ST_GeomFromText('POINT(150 150)')) as point_test,
  ST_Contains(
    ST_GeomFromText('POLYGON((100 100, 200 100, 200 200, 100 200, 100 100))'),
    ST_GeomFromText('POINT(150 150)')
  ) as point_in_polygon_test;
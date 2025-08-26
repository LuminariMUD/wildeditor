-- Migration: Add region hints tables for dynamic description system
-- Date: 2025-08-26
-- Description: Creates tables for storing AI-generated hints and profiles for regions

-- Create region_hints table
CREATE TABLE IF NOT EXISTS region_hints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region_vnum INT NOT NULL,
    hint_category ENUM(
        'atmosphere',
        'fauna',
        'flora',
        'geography',
        'weather_influence',
        'resources',
        'landmarks',
        'sounds',
        'scents',
        'seasonal_changes',
        'time_of_day',
        'mystical'
    ) NOT NULL,
    hint_text TEXT NOT NULL,
    priority INT DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    seasonal_weight JSON DEFAULT NULL,
    weather_conditions VARCHAR(255) DEFAULT 'clear,cloudy,rainy,stormy,lightning',
    time_of_day_weight JSON DEFAULT NULL,
    resource_triggers JSON DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Foreign key constraint
    CONSTRAINT fk_region_hints_vnum 
        FOREIGN KEY (region_vnum) 
        REFERENCES region_data(vnum) 
        ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_region_category (region_vnum, hint_category),
    INDEX idx_priority (priority),
    INDEX idx_active (is_active),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create region_profiles table
CREATE TABLE IF NOT EXISTS region_profiles (
    region_vnum INT PRIMARY KEY,
    overall_theme TEXT,
    dominant_mood VARCHAR(100),
    key_characteristics JSON,
    description_style ENUM('poetic', 'practical', 'mysterious', 'dramatic', 'pastoral') DEFAULT 'poetic',
    complexity_level INT DEFAULT 3 CHECK (complexity_level >= 1 AND complexity_level <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_region_profiles_vnum 
        FOREIGN KEY (region_vnum) 
        REFERENCES region_data(vnum) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create hint_usage_log table (optional - for analytics)
CREATE TABLE IF NOT EXISTS hint_usage_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hint_id INT NOT NULL,
    room_vnum INT NOT NULL,
    player_id INT DEFAULT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weather_condition VARCHAR(20),
    season VARCHAR(10),
    time_of_day VARCHAR(10),
    resource_state JSON DEFAULT NULL,
    
    -- Foreign key constraint
    CONSTRAINT fk_hint_usage_hint_id 
        FOREIGN KEY (hint_id) 
        REFERENCES region_hints(id) 
        ON DELETE CASCADE,
    
    -- Indexes for analytics
    INDEX idx_hint_usage (hint_id, used_at),
    INDEX idx_room_usage (room_vnum, used_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add sample data for testing (optional)
-- This can be commented out for production
/*
INSERT INTO region_hints (region_vnum, hint_category, hint_text, priority)
VALUES 
    (63001, 'atmosphere', 'The ancient trees tower overhead, their gnarled branches creating a natural cathedral.', 8),
    (63001, 'fauna', 'A family of deer can be glimpsed through the underbrush, their eyes watchful.', 6),
    (63001, 'sounds', 'The forest whispers with the rustle of leaves and distant bird calls.', 7);
*/

-- Grant necessary permissions (adjust user as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON region_hints TO 'wildeditor_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON region_profiles TO 'wildeditor_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON hint_usage_log TO 'wildeditor_user'@'%';
# Wildeditor AI MCP Foundation Planning

## Current State Analysis

### What We Have Access To
**Database Tables:**
- `region_data` - Polygon regions with types, properties, names
- `path_data` - Linear features (roads, rivers) as linestrings
- Basic spatial MySQL functions (ST_Contains, ST_Distance, etc.)

**Current MCP Server Tools:**
- `analyze_region` - Get region details by ID
- `find_path` - Pathfinding between regions  
- `search_regions` - Search by basic criteria
- `create_region` - Create new regions
- `validate_connections` - Check region connectivity

**Current MCP Server Resources:**
- `terrain-types` - Static terrain reference
- `environment-types` - Static environment reference  
- `region-stats` - Basic statistics
- `schema` - System schema
- `recent-regions` - Recently modified regions
- `capabilities` - System capabilities
- `map-overview` - High-level map view

### What We DON'T Have Access To
**Game Engine Data (C Server):**
- Perlin noise generation (elevation, moisture, temperature)
- Dynamic terrain calculation at specific coordinates
- Real-time weather patterns
- Zone entrance locations in wilderness
- Dynamic room pool status
- Player movement patterns
- Actual terrain type at any given X,Y coordinate
- KD-tree spatial indexing data

**Critical Gap:** The game engine has the sophisticated terrain generation system, but none of that computed data is available through the database.

## Foundation Requirements for AI Wilderness Editor

### Phase 1: Essential Data Bridge (High Priority)

#### 1. Terrain Data Snapshots
**Goal:** Make basic terrain information available to AI agents

**Game Engine Changes Needed:**
```c
// New table to store terrain samples
CREATE TABLE terrain_samples (
    x INT,
    y INT,
    elevation TINYINT UNSIGNED,    -- 0-255 from noise
    moisture TINYINT UNSIGNED,     -- 0-255 from noise  
    temperature TINYINT,           -- -30 to +35 calculated
    sector_type TINYINT UNSIGNED,  -- Final calculated terrain type
    weather_base TINYINT UNSIGNED, -- Base weather value
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (x, y),
    INDEX idx_sector (sector_type),
    INDEX idx_elevation (elevation)
);
```

**Implementation Strategy:**
- Sample terrain at regular intervals (every 10 coordinates?)
- Update samples periodically or on-demand
- Provide API endpoint to get terrain at coordinates
- Allow interpolation between sample points

#### 2. Zone Entrance Data
**Goal:** AI needs to know where players can enter/exit wilderness

**Game Engine Changes Needed:**
```c
// New table for zone entrances
CREATE TABLE wilderness_entrances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_vnum INT,
    wilderness_x INT,
    wilderness_y INT,
    room_vnum INT,           -- Room that leads to wilderness
    direction VARCHAR(10),   -- Direction from room to wilderness
    entrance_type ENUM('zone_exit', 'portal', 'teleport'),
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    INDEX idx_wilderness_coords (wilderness_x, wilderness_y),
    INDEX idx_zone (zone_vnum)
);
```

**Data Population:**
- Scan existing zones for exits to room 1000000 (wilderness nav room)
- Record coordinate destinations
- Update when zones are modified

#### 3. Basic Wilderness Metadata
**Goal:** System-level information for AI planning

**Game Engine Changes Needed:**
```c
// Wilderness system configuration
CREATE TABLE wilderness_config (
    setting_name VARCHAR(50) PRIMARY KEY,
    setting_value VARCHAR(255),
    setting_type ENUM('int', 'string', 'float'),
    description TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

// Pre-populate with key settings
INSERT INTO wilderness_config VALUES
('wild_x_size', '2048', 'int', 'Wilderness width'),
('wild_y_size', '2048', 'int', 'Wilderness height'),
('waterline', '128', 'int', 'Water level threshold'),
('dynamic_room_start', '1004000', 'int', 'Dynamic room pool start'),
('dynamic_room_end', '1009999', 'int', 'Dynamic room pool end');
```

### Phase 2: Enhanced Spatial Intelligence (Medium Priority)

#### 1. Points of Interest System
**Goal:** AI can understand and create meaningful landmarks

**Game Engine Changes Needed:**
```c
CREATE TABLE wilderness_poi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    x INT,
    y INT,
    name VARCHAR(100),
    type VARCHAR(50),        -- landmark, ruins, shrine, etc.
    visibility_range INT,    -- How far away it can be seen
    description TEXT,
    special_properties TEXT, -- JSON or delimited special flags
    created_by VARCHAR(50),  -- Who/what created it
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_coords (x, y),
    INDEX idx_type (type)
);
```

#### 2. Travel Difficulty Matrix
**Goal:** AI understands movement costs between terrain types

**Database Addition (No C Code Changes):**
```sql
CREATE TABLE terrain_movement (
    from_sector TINYINT UNSIGNED,
    to_sector TINYINT UNSIGNED,
    base_movement_cost DECIMAL(3,2),
    weather_modifier DECIMAL(3,2),
    special_requirements TEXT, -- swimming, climbing, etc.
    PRIMARY KEY (from_sector, to_sector)
);
```

### Phase 3: Advanced Features (Lower Priority)

#### 1. Historical Event Tracking
```sql
CREATE TABLE wilderness_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50),
    affected_area POLYGON,
    start_time DATETIME,
    duration_hours INT,
    description TEXT,
    game_effects TEXT,
    SPATIAL INDEX(affected_area)
);
```

#### 2. Resource Distribution
```sql
CREATE TABLE harvestable_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_type VARCHAR(50),
    sector_types TEXT,       -- Which terrain types it appears in
    abundance_modifier DECIMAL(3,2),
    seasonal_variation BOOLEAN,
    special_conditions TEXT
);
```

## Implementation Priorities

### Week 1-2: Database Foundation
1. **Create terrain_samples table** - Essential for AI terrain understanding
2. **Create wilderness_entrances table** - Critical for navigation planning
3. **Create wilderness_config table** - Basic system metadata

### Week 3-4: Game Engine Integration
1. **Implement terrain sampling function** in C code
2. **Add zone scanning for wilderness entrances**
3. **Create update routines** for maintaining data freshness

### Week 5-6: API Enhancement
1. **Add backend endpoints** for new data access
2. **Enhance MCP server tools** to use real terrain data
3. **Test AI agent integration** with actual game data

## Critical Technical Decisions

### 1. Terrain Sampling Strategy
**Options:**
- **Full Grid:** Sample every coordinate (4M+ records)
- **Sparse Grid:** Sample every 5-10 coordinates (40K-160K records)
- **On-Demand:** Calculate and cache when requested
- **Hybrid:** Pre-sample key areas, on-demand for others

**Recommendation:** Start with sparse grid (every 10 coordinates) = ~40K records

### 2. Data Freshness Strategy
**Options:**
- **Static:** Generate once, rarely update
- **Periodic:** Regenerate on schedule (daily/weekly)
- **Event-Based:** Update when game changes (new regions, etc.)
- **Real-Time:** Calculate every request (too expensive)

**Recommendation:** Periodic updates with event-based invalidation

### 3. C Code Integration Points
**Required Game Engine Hooks:**
```c
// Add to wilderness.c
void sample_terrain_to_database(int x, int y);
void update_wilderness_entrance_data(void);
void populate_terrain_samples_grid(int spacing);

// Add to boot sequence
void initialize_wilderness_database_sync(void);
```

## Backend API Extensions Needed

### New Endpoints Required
```python
# Terrain analysis (uses terrain_samples table)
GET /api/terrain/at-coordinates?x={x}&y={y}
GET /api/terrain/area?min_x={x}&max_x={x}&min_y={y}&max_y={y}

# Wilderness navigation
GET /api/wilderness/entrances
GET /api/wilderness/config

# Points of interest
GET /api/poi
POST /api/poi
GET /api/poi/near?x={x}&y={y}&radius={r}

# Enhanced spatial queries
GET /api/regions/at-point?x={x}&y={y}
GET /api/paths/near?x={x}&y={y}&radius={r}
```

## Success Metrics

### Phase 1 Success Criteria
- [ ] AI can query actual terrain type at any coordinate
- [ ] AI knows where players can enter wilderness from zones
- [ ] AI has access to basic wilderness system parameters
- [ ] Backend API provides real game data (not mock data)

### Phase 2 Success Criteria  
- [ ] AI can plan routes considering terrain difficulty
- [ ] AI can create and manage points of interest
- [ ] AI understands spatial relationships between features

### Phase 3 Success Criteria
- [ ] AI can track and respond to historical events
- [ ] AI understands resource distribution patterns
- [ ] AI can make intelligent content placement decisions

## Next Steps

1. **Review and approve** this foundation plan
2. **Prioritize** which Phase 1 items to implement first
3. **Design detailed database schemas** for chosen items
4. **Plan C code integration points** for game engine changes
5. **Create development timeline** with realistic milestones

This foundation approach ensures that AI agents will have access to real game data while maintaining security and system stability through database-mediated access.

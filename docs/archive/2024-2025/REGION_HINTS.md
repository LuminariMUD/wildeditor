# Region Hints System Documentation

## Overview

The Region Hints System is a comprehensive feature that enhances the dynamic description engine by providing contextual, categorized hints that can be used to generate varied and immersive descriptions for wilderness regions. These hints are extracted from AI-generated region descriptions and stored in a structured format with metadata for contextual usage.

## Architecture

### Database Schema

The system uses three main database tables:

#### 1. `region_hints`
Stores individual hints with categorization and contextual metadata.

- **Fields:**
  - `id`: Primary key
  - `region_vnum`: Foreign key to region_data
  - `hint_category`: Category enum (atmosphere, fauna, flora, etc.)
  - `hint_text`: The descriptive text
  - `priority`: 1-10 usage frequency
  - `seasonal_weight`: JSON seasonal multipliers
  - `weather_conditions`: Applicable weather conditions
  - `time_of_day_weight`: JSON time-based multipliers
  - `resource_triggers`: JSON resource conditions
  - `ai_agent_id`: Source AI agent
  - `created_at`, `updated_at`: Timestamps
  - `is_active`: Active status flag

#### 2. `region_profiles`
Stores personality profiles for regions to ensure consistency.

- **Fields:**
  - `region_vnum`: Primary key and foreign key
  - `overall_theme`: Text description of theme
  - `dominant_mood`: Primary atmosphere
  - `key_characteristics`: JSON array of features
  - `description_style`: Writing style enum
  - `complexity_level`: Detail level (1-5)
  - `ai_agent_id`: Source AI agent
  - `created_at`, `updated_at`: Timestamps

#### 3. `hint_usage_log`
Tracks hint usage for analytics and optimization.

- **Fields:**
  - `id`: Primary key
  - `hint_id`: Foreign key to region_hints
  - `room_vnum`: Room where hint was used
  - `player_id`: Optional player tracking
  - `used_at`: Usage timestamp
  - `weather_condition`: Weather at time
  - `season`: Season at time
  - `time_of_day`: Time at use
  - `resource_state`: JSON resource snapshot

### Hint Categories

The system supports 12 hint categories:

1. **atmosphere** - Overall mood and feeling
2. **fauna** - Animal and creature descriptions
3. **flora** - Plant and vegetation descriptions
4. **geography** - Terrain and geological features
5. **weather_influence** - Weather-specific details
6. **resources** - Available materials and resources
7. **landmarks** - Notable features and structures
8. **sounds** - Ambient sounds and noises
9. **scents** - Smells and aromas
10. **seasonal_changes** - Season-specific variations
11. **time_of_day** - Time-based changes
12. **mystical** - Magical and supernatural elements

## API Endpoints

### Hint Management

#### GET `/api/regions/{vnum}/hints`
List all hints for a region.

**Query Parameters:**
- `category`: Filter by category
- `is_active`: Filter by active status
- `min_priority`: Minimum priority filter

**Response:**
```json
{
  "hints": [...],
  "total_count": 20,
  "active_count": 18,
  "categories": {
    "atmosphere": 5,
    "fauna": 3,
    "flora": 4,
    ...
  }
}
```

#### POST `/api/regions/{vnum}/hints`
Create hints for a region (supports batch creation).

**Request Body:**
```json
{
  "hints": [
    {
      "hint_category": "atmosphere",
      "hint_text": "Crystal formations cast prismatic light...",
      "priority": 8,
      "seasonal_weight": {"spring": 1.0, ...},
      "weather_conditions": ["clear", "cloudy"]
    }
  ]
}
```

#### PUT `/api/regions/{vnum}/hints/{id}`
Update a specific hint.

#### DELETE `/api/regions/{vnum}/hints/{id}`
Delete a specific hint.

### Profile Management

#### GET `/api/regions/{vnum}/profile`
Get the personality profile for a region.

#### POST `/api/regions/{vnum}/profile`
Create or update a region's profile.

**Request Body:**
```json
{
  "overall_theme": "An underground crystal cavern...",
  "dominant_mood": "mystical_wonder",
  "key_characteristics": ["crystal_formations", "echoing_chambers"],
  "description_style": "mysterious",
  "complexity_level": 4
}
```

### Hint Generation

#### POST `/api/regions/{vnum}/hints/generate`
Generate hints from a region description using AI.

**Request Body:**
```json
{
  "description": "The Crystal Caverns are a magnificent...",
  "region_name": "Crystal Caverns",
  "region_type": 1,
  "target_hint_count": 15,
  "include_profile": true
}
```

### Analytics

#### GET `/api/regions/{vnum}/hints/analytics`
Get usage analytics for a region's hints.

## MCP Tools

The MCP server provides three main tools for hint management:

### 1. `generate_hints_from_description`
Analyzes a region description and generates categorized hints.

**Parameters:**
- `region_vnum`: VNUM of region (optional)
- `description`: Description text to analyze
- `region_name`: Name of the region
- `target_hint_count`: Number of hints to generate (5-30)
- `include_profile`: Generate profile (boolean)

**Process:**
1. Parses description into sentences
2. Categorizes based on keyword patterns
3. Assigns priority based on quality
4. Determines weather conditions
5. Calculates seasonal/time weights
6. Generates region profile if requested

### 2. `store_region_hints`
Stores generated hints in the database.

**Parameters:**
- `region_vnum`: Target region VNUM
- `hints`: Array of hint objects
- `profile`: Optional profile object

### 3. `get_region_hints`
Retrieves existing hints for a region.

**Parameters:**
- `region_vnum`: Region VNUM
- `category`: Optional category filter
- `active_only`: Only active hints (boolean)

## Hint Generation Process

### 1. Description Analysis
The system analyzes descriptions using pattern matching:

```python
category_patterns = {
    "atmosphere": ["atmosphere", "feeling", "mood", ...],
    "fauna": ["animal", "creature", "bird", ...],
    "flora": ["tree", "plant", "flower", ...],
    ...
}
```

### 2. Priority Calculation
Priority (1-10) is calculated based on:
- Sentence length (>100 chars: +1)
- Descriptive language (vivid words: +1)
- Sentence complexity (multiple clauses: +1)

### 3. Weather Determination
Weather conditions are determined by keywords:
- `clear`: "sun", "bright", "clear sky"
- `cloudy`: "cloud", "overcast", "grey sky"
- `rainy`: "rain", "drizzle", "wet"
- `stormy`: "storm", "thunder", "tempest"
- `lightning`: "lightning", "electric", "flash"

### 4. Seasonal Weights
Seasonal multipliers (0.0-2.0) based on content:
- Spring keywords: "bloom", "blossom", "spring"
- Summer keywords: "hot", "warm", "summer"
- Autumn keywords: "fall", "leaves", "autumn"
- Winter keywords: "snow", "cold", "winter"

### 5. Time-of-Day Weights
Time multipliers based on content:
- Dawn: "sunrise", "dawn"
- Morning: "morning"
- Midday: "noon", "midday"
- Evening: "dusk", "sunset", "evening"
- Night: "darkness", "moonlight", "night"

## Usage Example

### Complete Workflow

1. **Generate Region Description**
```javascript
// Generate description for region
const description = await generateRegionDescription({
  region_vnum: 9999001,
  region_name: "Crystal Caverns",
  style: "mysterious",
  length: "detailed"
});
```

2. **Extract Hints from Description**
```javascript
// Use MCP tool to generate hints
const hintsResult = await mcpClient.callTool('generate_hints_from_description', {
  region_vnum: 9999001,
  description: description.text,
  target_hint_count: 20,
  include_profile: true
});
```

3. **Store Hints in Database**
```javascript
// Store the generated hints
const storeResult = await mcpClient.callTool('store_region_hints', {
  region_vnum: 9999001,
  hints: hintsResult.hints,
  profile: hintsResult.profile
});
```

4. **Dynamic Description Engine Usage**
```javascript
// Game engine retrieves hints based on context
const hints = await getRegionHints({
  region_vnum: 9999001,
  category: 'atmosphere',
  weather: 'cloudy',
  season: 'autumn',
  time: 'evening'
});

// Select hints based on priority and weights
const selectedHint = selectWeightedHint(hints);
```

## Test Region: Crystal Caverns

For testing purposes, use region VNUM 9999001:

```sql
-- Create test region
INSERT INTO region_data (vnum, name, region_type, zone_vnum) 
VALUES (9999001, 'The Crystal Caverns', 1, 999);
```

Example hints for Crystal Caverns:
- **Atmosphere**: "Crystalline formations cast prismatic light throughout the cavern..."
- **Sounds**: "The gentle ping of water droplets echoes musically..."
- **Flora**: "Bioluminescent fungi cling to the crystal formations..."
- **Geography**: "Massive crystal columns stretch from floor to ceiling..."

## Benefits

1. **Dynamic Descriptions**: Each visit can have different descriptive elements
2. **Contextual Awareness**: Hints activate based on environmental conditions
3. **Consistent Theme**: Profiles ensure atmospheric coherence
4. **Performance**: Pre-generated hints reduce runtime computation
5. **Quality**: AI-generated content maintains high narrative standards
6. **Analytics**: Usage tracking enables optimization

## Integration Points

### Frontend
- Region editor can display hints
- Preview dynamic descriptions
- Manage hint priorities

### Game Engine
- Query hints by context
- Weight-based selection
- Fallback to defaults
- Performance caching

### AI Services
- Generate new hints
- Update existing hints
- Quality assessment
- Style consistency

## Performance Considerations

- Indexed by region_vnum and category
- Cached at game server level
- Batch operations supported
- Async generation available
- Usage logging optional

## Future Enhancements

1. **Player Personalization**: Track player preferences
2. **Learning System**: Adjust weights based on usage
3. **Multi-language Support**: Hints in multiple languages
4. **Procedural Variation**: Combine hints dynamically
5. **Quality Scoring**: AI-based quality assessment
6. **Version Control**: Track hint changes over time

## Troubleshooting

### Common Issues

**No hints generated:**
- Check description length (min 100 chars)
- Verify region exists in database
- Check MCP server connectivity

**Hints not displaying:**
- Verify is_active flag
- Check weather/time filters
- Review priority settings

**Performance issues:**
- Add database indexes
- Enable caching layer
- Limit hint count per region

## API Reference

See `/api/docs` for complete OpenAPI documentation of all endpoints.

## Database Migrations

Run migrations to create hint tables:
```sql
source ~/Luminari-Source/sql/ai_region_hints_schema.sql
```

## Configuration

Environment variables:
- `AI_PROVIDER`: AI service for generation
- `HINT_CACHE_TTL`: Cache timeout (seconds)
- `MAX_HINTS_PER_REGION`: Limit hint count

---

*Last Updated: 2024*
*Version: 1.0.0*
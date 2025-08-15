# Test Commands for New Terrain Bridge API Endpoints
# Server: luminarimud.com:8000 (Backend API)
# Authentication: X-API-Key header required

# Set variables for easier testing
API_KEY="your_api_key_here"
BASE_URL="http://luminarimud.com:8000"

# ===========================================
# TERRAIN ENDPOINTS
# ===========================================

# Test 1: Get terrain at origin (0,0)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/at-coordinates?x=0&y=0"

# Test 2: Get terrain at specific coordinates  
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/at-coordinates?x=100&y=-50"

# Test 3: Get terrain at mountain coordinates
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/at-coordinates?x=200&y=300"

# Test 4: Batch terrain data (small area)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/batch?x_min=0&y_min=0&x_max=5&y_max=5"

# Test 5: Batch terrain data (larger area for mapping)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/batch?x_min=-10&y_min=-10&x_max=10&y_max=10"

# Test 6: Test coordinate bounds (should work)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/at-coordinates?x=1024&y=-1024"

# Test 7: Test coordinate bounds (should fail)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/at-coordinates?x=1025&y=0"

# ===========================================
# WILDERNESS ROOM ENDPOINTS  
# ===========================================

# Test 8: List first 10 wilderness rooms
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/wilderness/rooms?limit=10"

# Test 9: List more wilderness rooms
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/wilderness/rooms?limit=50"

# Test 10: Get details for navigation room (room 1000000)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/wilderness/rooms/1000000"

# Test 11: Get details for another wilderness room
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/wilderness/rooms/1000123"

# Test 12: Test room that might not exist
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/wilderness/rooms/9999999"

# ===========================================
# RESPONSE FORMAT EXAMPLES
# ===========================================

# Expected terrain response:
# {
#   "success": true,
#   "data": {
#     "x": 0,
#     "y": 0,
#     "elevation": 135,
#     "temperature": 27,
#     "moisture": 127,
#     "sector_type": 2,
#     "sector_name": "Field"
#   }
# }

# Expected batch terrain response:
# {
#   "success": true,
#   "count": 36,
#   "data": [
#     {"x": 0, "y": 0, "elevation": 135, "temperature": 27, "moisture": 127, "sector_type": 2, "sector_name": "Field"},
#     {"x": 0, "y": 1, "elevation": 140, "temperature": 26, "moisture": 130, "sector_type": 3, "sector_name": "Forest"},
#     ...
#   ]
# }

# Expected room list response:
# {
#   "success": true,
#   "total_rooms": 50,
#   "data": [
#     {
#       "vnum": 1000000,
#       "name": "The Wilderness",
#       "x": 0,
#       "y": 0,
#       "sector_type": "Inside",
#       "zone_name": "Wilderness of Luminari",
#       "zone_vnum": 10000
#     },
#     ...
#   ]
# }

# Expected room details response:
# {
#   "success": true,
#   "data": {
#     "vnum": 1000123,
#     "name": "Near a Cave Entrance",
#     "description": "A sharp slant downward...",
#     "x": 3,
#     "y": 4,
#     "sector_type": "Zone Entrance",
#     "zone": {
#       "name": "Wilderness of Luminari",
#       "vnum": 10000
#     },
#     "exits": [
#       {
#         "direction": "north",
#         "to_room_vnum": 1000000,
#         "to_room_sector_type": "Inside"
#       },
#       {
#         "direction": "down", 
#         "to_room_vnum": 40600,
#         "to_room_sector_type": "Inside"
#       }
#     ],
#     "room_flags_0": 0,
#     "room_flags_1": 0,
#     "room_flags_2": 0,
#     "room_flags_3": 0
#   }
# }

# ===========================================
# ERROR TESTING
# ===========================================

# Test 13: Missing coordinates
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/at-coordinates"

# Test 14: Invalid coordinates (out of bounds)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/at-coordinates?x=2000&y=2000"

# Test 15: Invalid batch range (too large)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/batch?x_min=-100&y_min=-100&x_max=100&y_max=100"

# Test 16: Missing authentication
curl "$BASE_URL/api/terrain/at-coordinates?x=0&y=0"

# ===========================================
# PERFORMANCE TESTING
# ===========================================

# Test 17: Large batch request (near maximum)
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/batch?x_min=0&y_min=0&x_max=31&y_max=31"
# This should return 32x32 = 1024 coordinates (near the 1000 limit)

# Test 18: Multiple rapid requests (test caching)
for i in {1..5}; do
  echo "Request $i:"
  curl -s -H "X-API-Key: $API_KEY" \
    "$BASE_URL/api/terrain/at-coordinates?x=0&y=0" | jq '.data.elevation'
done

# ===========================================
# INTEGRATION TESTING WITH MCP SERVER
# ===========================================

# These test the MCP server tools that use the new backend endpoints

# Test 19: MCP terrain analysis tool
curl -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"x": 0, "y": 0, "include_noise_layers": true}' \
  "http://luminarimud.com:8001/mcp/tools/analyze_terrain_at_coordinates"

# Test 20: MCP wilderness rooms tool
curl -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}' \
  "http://luminarimud.com:8001/mcp/tools/get_wilderness_rooms"

# Test 21: MCP room details tool
curl -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"vnum": 1000000}' \
  "http://luminarimud.com:8001/mcp/tools/get_room_details"

# Test 22: MCP terrain map generation
curl -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"center_x": 0, "center_y": 0, "radius": 5}' \
  "http://luminarimud.com:8001/mcp/tools/generate_terrain_map"

# ===========================================
# USEFUL ONE-LINERS FOR EXPLORATION
# ===========================================

# Find interesting terrain types
curl -s -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/terrain/batch?x_min=-50&y_min=-50&x_max=50&y_max=50" | \
  jq '.data | group_by(.sector_name) | map({sector: .[0].sector_name, count: length})'

# Get elevation profile along a line
for x in {0..10}; do
  curl -s -H "X-API-Key: $API_KEY" \
    "$BASE_URL/api/terrain/at-coordinates?x=$x&y=0" | \
    jq -r ".data | \"($x,0): elevation=\(.elevation), terrain=\(.sector_name)\""
done

# Find all wilderness rooms with exits to other zones
curl -s -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/wilderness/rooms?limit=100" | \
  jq '.data[] | select(.sector_type == "Zone Entrance")'

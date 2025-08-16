# PowerShell Test Commands for New Terrain Bridge API Endpoints
# Server: luminarimud.com:8000 (Backend API)
# Authenticat# Test 18: Missing coordinates
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for missing coordinates: $($_.Exception.Message)"
}

# Test 19: Missing authentication
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0&y=0"
} catch {
    Write-Host "Expected error for missing auth: $($_.Exception.Message)"
}

# Test 20: Invalid batch range (too large)
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=-100&y_min=-100&x_max=100&y_max=100" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for batch too large: $($_.Exception.Message)"
}r required

# Set variables for easier testing
$API_KEY = "0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"
$BASE_URL = "http://luminarimud.com:8000"
$MCP_API_KEY = "xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="
$MCP_URL = "http://luminarimud.com:8001"

# ===========================================
# TERRAIN ENDPOINTS
# ===========================================

# Test 1: Get terrain at origin (0,0)
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0`&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 2: Get terrain at specific coordinates  
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=100&y=-50" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 3: Get terrain at mountain coordinates
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=200&y=300" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 4: Batch terrain data (small area)
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=0&y_min=0&x_max=5&y_max=5" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 5: Batch terrain data (larger area for mapping)
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=-10&y_min=-10&x_max=10&y_max=10" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 6: Test coordinate bounds (should work)
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=1024&y=-1024" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 7: Test coordinate bounds (should fail gracefully)
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=1025&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for out-of-bounds coordinates: $($_.Exception.Message)"
}

# ===========================================
# WILDERNESS ROOM ENDPOINTS  
# ===========================================

# Test 8: List first 10 wilderness rooms
Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms?limit=10" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 9: List more wilderness rooms
Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms?limit=50" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 10: Get details for navigation room (room 1000000)
Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms/1000000" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 11: Get details for another wilderness room
Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms/1000123" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Test 12: Test room that might not exist
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms/9999999" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for non-existent room: $($_.Exception.Message)"
}

# ===========================================
# MCP SERVER INTEGRATION TESTING
# ===========================================

# Test 13: MCP terrain analysis tool
$terrainBody = @{
    x = 0
    y = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" `
    -Method POST `
    -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
    -Body $terrainBody

# Test 14: MCP wilderness room finder tool
$roomsBody = @{
    x = 0
    y = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_wilderness_room" `
    -Method POST `
    -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
    -Body $roomsBody

# Test 15: MCP room details by VNUM tool
$roomDetailsBody = @{
    vnum = 1000000
} | ConvertTo-Json

Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_wilderness_room" `
    -Method POST `
    -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
    -Body $roomDetailsBody

# Test 16: MCP wilderness map generation
$mapBody = @{
    center_x = 0
    center_y = 0
    radius = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/generate_wilderness_map" `
    -Method POST `
    -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
    -Body $mapBody

# Test 17: MCP zone entrances finder (NEW)
Write-Host "`nTesting MCP zone entrances tool..." -ForegroundColor Yellow
$zoneEntrancesResult = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_zone_entrances" `
    -Method POST `
    -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
    -Body "{}"

Write-Host "✓ Found $($zoneEntrancesResult.result.entrance_count) zone entrances in wilderness" -ForegroundColor Green
Write-Host "✓ Total wilderness exit rooms: $($zoneEntrancesResult.result.total_wilderness_rooms)" -ForegroundColor Green

# ===========================================
# ERROR TESTING
# ===========================================

# Test 18: Missing coordinates
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for missing coordinates: $($_.Exception.Message)"
}

# Test 18: Missing authentication
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0&y=0"
} catch {
    Write-Host "Expected error for missing auth: $($_.Exception.Message)"
}

# Test 19: Invalid batch range (too large)
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=-100&y_min=-100&x_max=100&y_max=100" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for batch too large: $($_.Exception.Message)"
}

# ===========================================
# PERFORMANCE TESTING
# ===========================================

# Test 20: Large batch request (near maximum)
Write-Host "Testing large batch request (32x32 = 1024 coordinates)..."
$largeBatch = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=0&y_min=0&x_max=31&y_max=31" -Headers @{"Authorization" = "Bearer $API_KEY"}
Write-Host "Received $($largeBatch.count) terrain points"

# Test 21: Multiple rapid requests (test caching)
Write-Host "Testing multiple rapid requests for caching..."
for ($i = 1; $i -le 5; $i++) {
    $start = Get-Date
    $result = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}
    $end = Get-Date
    $duration = ($end - $start).TotalMilliseconds
    Write-Host "Request ${i}: elevation=$($result.data.elevation), time=$($duration)ms"
}

# ===========================================
# HELPER FUNCTIONS FOR EXPLORATION
# ===========================================

# Function: Get terrain summary for an area
function Get-TerrainSummary {
    param(
        [int]$MinX = -10,
        [int]$MaxX = 10,
        [int]$MinY = -10,
        [int]$MaxY = 10
    )
    
    $terrain = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=$MinX&y_min=$MinY&x_max=$MaxX&y_max=$MaxY" -Headers @{"Authorization" = "Bearer $API_KEY"}
    
    $summary = $terrain.data | Group-Object sector_name | Select-Object @{N='Terrain';E={$_.Name}}, @{N='Count';E={$_.Count}} | Sort-Object Count -Descending
    
    Write-Host "Terrain Summary for area ($MinX,$MinY) to ($MaxX,$MaxY):"
    $summary | Format-Table -AutoSize
    
    return $terrain
}

# Function: Get elevation profile along a line
function Get-ElevationProfile {
    param(
        [int]$StartX = 0,
        [int]$StartY = 0,
        [int]$EndX = 10,
        [int]$EndY = 0
    )
    
    Write-Host "Elevation profile from ($StartX,$StartY) to ($EndX,$EndY):"
    
    for ($x = $StartX; $x -le $EndX; $x++) {
        $terrain = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=$x&y=$StartY" -Headers @{"Authorization" = "Bearer $API_KEY"}
        Write-Host "($x,$StartY): elevation=$($terrain.data.elevation), terrain=$($terrain.data.sector_name)"
    }
}

# Function: Find zone entrances
function Get-ZoneEntrances {
    $rooms = Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms?limit=100" -Headers @{"Authorization" = "Bearer $API_KEY"}
    
    $entrances = $rooms.data | Where-Object { $_.sector_type -eq "Zone Entrance" }
    
    Write-Host "Found $($entrances.Count) zone entrances:"
    $entrances | Select-Object vnum, name, x, y | Format-Table -AutoSize
    
    return $entrances
}

# ===========================================
# QUICK TEST SUITE
# ===========================================

function Run-QuickTests {
    Write-Host "=== Running Quick Test Suite ===" -ForegroundColor Green
    
    # Test 1: Health check
    Write-Host "`n1. Testing API health..." -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "$BASE_URL/api/health"
        Write-Host "✓ API is healthy: $($health.status)" -ForegroundColor Green
    } catch {
        Write-Host "✗ API health check failed: $($_.Exception.Message)" -ForegroundColor Red
        return
    }
    
    # Test 2: Basic terrain
    Write-Host "`n2. Testing basic terrain query..." -ForegroundColor Yellow
    try {
        $terrain = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}
        Write-Host "✓ Terrain at (0,0): $($terrain.data.sector_name), elevation=$($terrain.data.elevation)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Terrain query failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 3: Room list
    Write-Host "`n3. Testing wilderness rooms..." -ForegroundColor Yellow
    try {
        $rooms = Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms?limit=5" -Headers @{"Authorization" = "Bearer $API_KEY"}
        Write-Host "✓ Found $($rooms.total_rooms) wilderness rooms" -ForegroundColor Green
    } catch {
        Write-Host "✗ Room list failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 4: MCP integration
    Write-Host "`n4. Testing MCP integration..." -ForegroundColor Yellow
    try {
        $mcpBody = @{ x = 0; y = 0 } | ConvertTo-Json
        $mcpResult = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" `
            -Method POST `
            -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
            -Body $mcpBody
        Write-Host "✓ MCP terrain analysis successful" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP integration failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`n=== Quick Test Suite Complete ===" -ForegroundColor Green
}

# ===========================================
# USAGE EXAMPLES
# ===========================================

<#
# Run the quick test suite
Run-QuickTests

# Get terrain summary for a small area
Get-TerrainSummary -MinX 0 -MaxX 10 -MinY 0 -MaxY 10

# Get elevation profile along X axis
Get-ElevationProfile -StartX -10 -EndX 10

# Find all zone entrances
Get-ZoneEntrances

# Test specific coordinates
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=100`&y=-200" -Headers @{"Authorization" = "Bearer $API_KEY"}

# Get detailed room info
Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/rooms/1000000" -Headers @{"Authorization" = "Bearer $API_KEY"}
#>

Write-Host "Terrain Bridge API Test Commands Loaded!" -ForegroundColor Cyan
Write-Host "Run 'Run-QuickTests' to start basic testing" -ForegroundColor Cyan
Write-Host "Make sure to set your API_KEY variable first: `$API_KEY = 'your_actual_key'" -ForegroundColor Yellow

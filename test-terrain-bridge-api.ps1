# PowerShell Test Commands for New Terrain Bridge API Endpoints
# Server: luminarimud.com:8000 (Backend API)
# Authentication: X-API-Key header required

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
# MCP SERVER COMPREHENSIVE TESTING (17 CAPABILITIES)
# ===========================================

Write-Host "`n=== Testing All 10 MCP Tools ===" -ForegroundColor Cyan

# Tool 1: analyze_terrain_at_coordinates
Write-Host "1. Testing analyze_terrain_at_coordinates..." -ForegroundColor Yellow
$terrainBody = @{
    x = 0
    y = 0
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $terrainBody
    Write-Host "✓ Terrain at (0,0): $($result.result.terrain_data.sector_name)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 2: find_wilderness_room (by coordinates)
Write-Host "2. Testing find_wilderness_room (coordinates)..." -ForegroundColor Yellow
$roomCoordsBody = @{
    x = 0
    y = 0
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_wilderness_room" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $roomCoordsBody
    Write-Host "✓ Room at (0,0): VNUM $($result.result.room_data.vnum)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 3: find_wilderness_room (by VNUM)
Write-Host "3. Testing find_wilderness_room (VNUM)..." -ForegroundColor Yellow
$roomVnumBody = @{
    vnum = 1000000
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_wilderness_room" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $roomVnumBody
    Write-Host "✓ Room VNUM 1000000: '$($result.result.room_data.name)'" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 4: find_zone_entrances
Write-Host "4. Testing find_zone_entrances..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_zone_entrances" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body "{}"
    Write-Host "✓ Found $($result.result.entrance_count) zone entrances" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 5: generate_wilderness_map
Write-Host "5. Testing generate_wilderness_map..." -ForegroundColor Yellow
$mapBody = @{
    center_x = 0
    center_y = 0
    radius = 5
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/generate_wilderness_map" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $mapBody
    Write-Host "✓ Generated map: $($result.result.map_data.grid_size) grid" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 6: analyze_complete_terrain_map
Write-Host "6. Testing analyze_complete_terrain_map..." -ForegroundColor Yellow
$completeMapBody = @{
    center_x = 0
    center_y = 0
    radius = 3
    include_regions = $true
    include_paths = $true
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_complete_terrain_map" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $completeMapBody
    Write-Host "✓ Complete analysis: $($result.result.analysis.region_overlays.Count) regions, $($result.result.analysis.path_overlays.Count) paths" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 7: analyze_region
Write-Host "7. Testing analyze_region..." -ForegroundColor Yellow
$regionBody = @{
    region_id = 1
    include_paths = $true
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_region" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $regionBody
    Write-Host "✓ Region analysis completed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 8: search_regions
Write-Host "8. Testing search_regions..." -ForegroundColor Yellow
$searchBody = @{
    terrain_type = "forest"
    limit = 5
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/search_regions" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $searchBody
    Write-Host "✓ Search completed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 9: find_path
Write-Host "9. Testing find_path..." -ForegroundColor Yellow
$pathBody = @{
    from_region = 1
    to_region = 2
    max_distance = 5
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_path" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $pathBody
    Write-Host "✓ Path finding completed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Tool 10: validate_connections
Write-Host "10. Testing validate_connections..." -ForegroundColor Yellow
$validateBody = @{
    region_id = 1
    check_bidirectional = $true
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/validate_connections" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $validateBody
    Write-Host "✓ Connection validation completed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Testing All 7 MCP Resources ===" -ForegroundColor Cyan

# Resource 1: terrain-types
Write-Host "1. Testing terrain-types resource..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://terrain-types" `
        -Headers @{"X-API-Key" = $MCP_API_KEY}
    Write-Host "✓ Terrain types loaded: $($result.terrain_types.Count) types" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Resource 2: environment-types
Write-Host "2. Testing environment-types resource..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://environment-types" `
        -Headers @{"X-API-Key" = $MCP_API_KEY}
    Write-Host "✓ Environment types loaded: $($result.environment_types.Count) types" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Resource 3: region-stats
Write-Host "3. Testing region-stats resource..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://region-stats" `
        -Headers @{"X-API-Key" = $MCP_API_KEY}
    Write-Host "✓ Region statistics loaded: $($result.total_regions) regions" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Resource 4: schema
Write-Host "4. Testing schema resource..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://schema" `
        -Headers @{"X-API-Key" = $MCP_API_KEY}
    Write-Host "✓ Schema loaded: $($result.tables.Count) tables" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Resource 5: recent-regions
Write-Host "5. Testing recent-regions resource..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://recent-regions" `
        -Headers @{"X-API-Key" = $MCP_API_KEY}
    Write-Host "✓ Recent regions loaded: $($result.recent_regions.Count) regions" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Resource 6: capabilities
Write-Host "6. Testing capabilities resource..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://capabilities" `
        -Headers @{"X-API-Key" = $MCP_API_KEY}
    Write-Host "✓ Capabilities loaded: $($result.features.Count) features" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Resource 7: map-overview
Write-Host "7. Testing map-overview resource..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://map-overview" `
        -Headers @{"X-API-Key" = $MCP_API_KEY}
    Write-Host "✓ Map overview loaded: $($result.overview.total_area) total area" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# ===========================================
# ZONE ENTRANCE TESTING (NEW)
# ===========================================

# Test 17: Zone entrances endpoint (NEW)
Write-Host "Testing zone entrances endpoint..." -ForegroundColor Yellow
try {
    $entrances = Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/navigation/entrances" -Headers @{"Authorization" = "Bearer $API_KEY"}
    Write-Host "✓ Found $($entrances.entrance_count) zone entrances from $($entrances.total_wilderness_rooms) wilderness rooms" -ForegroundColor Green
    if ($entrances.entrance_count -gt 0) {
        $sample = $entrances.entrances[0]
        Write-Host "  Sample: Room $($sample.wilderness_room.vnum) at ($($sample.wilderness_room.x),$($sample.wilderness_room.y)) -> $($sample.zone_exits.Count) zones" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Zone entrances failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 18: MCP zone entrances tool (NEW)
Write-Host "Testing MCP zone entrances tool..." -ForegroundColor Yellow
try {
    $mcpResult = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_zone_entrances" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body "{}"
    Write-Host "✓ MCP found $($mcpResult.result.entrance_count) zone entrances" -ForegroundColor Green
} catch {
    Write-Host "✗ MCP zone entrances failed: $($_.Exception.Message)" -ForegroundColor Red
}

# ===========================================
# ERROR TESTING
# ===========================================

# Test 19: Missing coordinates
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for missing coordinates: $($_.Exception.Message)"
}

# Test 20: Missing authentication
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0`&y=0"
} catch {
    Write-Host "Expected error for missing auth: $($_.Exception.Message)"
}

# Test 21: Invalid batch range (too large)
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=-100`&y_min=-100`&x_max=100`&y_max=100" -Headers @{"Authorization" = "Bearer $API_KEY"}
} catch {
    Write-Host "Expected error for batch too large: $($_.Exception.Message)"
}

# ===========================================
# PERFORMANCE TESTING
# ===========================================

# Test 22: Large batch request (near maximum)
Write-Host "Testing large batch request (32x32 = 1024 coordinates)..."
$largeBatch = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/batch?x_min=0`&y_min=0`&x_max=31`&y_max=31" -Headers @{"Authorization" = "Bearer $API_KEY"}
Write-Host "Received $($largeBatch.count) terrain points"

# Test 23: Multiple rapid requests (test caching)
Write-Host "Testing multiple rapid requests for caching..."
for ($i = 1; $i -le 5; $i++) {
    $start = Get-Date
    $result = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0`&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}
    $end = Get-Date
    $duration = ($end - $start).TotalMilliseconds
    Write-Host "Request ${i}: elevation=$($result.data.elevation), time=$($duration)ms"
}

# ===========================================
# COMPREHENSIVE MCP TEST FUNCTIONS
# ===========================================

function Test-AllMCPTools {
    Write-Host "`n=== Testing All 10 MCP Tools ===" -ForegroundColor Cyan
    
    $successCount = 0
    $totalTools = 10
    
    # Tool 1: analyze_terrain_at_coordinates
    Write-Host "1. Testing analyze_terrain_at_coordinates..." -ForegroundColor Yellow
    try {
        $body = @{ x = 0; y = 0 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: $($result.result.terrain_data.sector_name)" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 2: find_wilderness_room (coordinates)
    Write-Host "2. Testing find_wilderness_room (coordinates)..." -ForegroundColor Yellow
    try {
        $body = @{ x = 0; y = 0 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_wilderness_room" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: Room VNUM $($result.result.room_data.vnum)" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 3: find_wilderness_room (VNUM)
    Write-Host "3. Testing find_wilderness_room (VNUM)..." -ForegroundColor Yellow
    try {
        $body = @{ vnum = 1000000 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_wilderness_room" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: '$($result.result.room_data.name)'" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 4: find_zone_entrances
    Write-Host "4. Testing find_zone_entrances..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_zone_entrances" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body "{}"
        Write-Host "   ✓ Success: $($result.result.entrance_count) entrances" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 5: generate_wilderness_map
    Write-Host "5. Testing generate_wilderness_map..." -ForegroundColor Yellow
    try {
        $body = @{ center_x = 0; center_y = 0; radius = 5 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/generate_wilderness_map" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: Generated $($result.result.map_data.grid_size) grid" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 6: analyze_complete_terrain_map
    Write-Host "6. Testing analyze_complete_terrain_map..." -ForegroundColor Yellow
    try {
        $body = @{ center_x = 0; center_y = 0; radius = 3; include_regions = $true; include_paths = $true } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_complete_terrain_map" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: Analysis with overlays completed" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 7: analyze_region
    Write-Host "7. Testing analyze_region..." -ForegroundColor Yellow
    try {
        $body = @{ region_id = 1; include_paths = $true } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_region" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: Region analysis completed" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 8: search_regions
    Write-Host "8. Testing search_regions..." -ForegroundColor Yellow
    try {
        $body = @{ terrain_type = "forest"; limit = 5 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/search_regions" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: Region search completed" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 9: find_path
    Write-Host "9. Testing find_path..." -ForegroundColor Yellow
    try {
        $body = @{ from_region = 1; to_region = 2; max_distance = 5 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_path" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: Path finding completed" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 10: validate_connections
    Write-Host "10. Testing validate_connections..." -ForegroundColor Yellow
    try {
        $body = @{ region_id = 1; check_bidirectional = $true } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/validate_connections" `
            -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body
        Write-Host "   ✓ Success: Connection validation completed" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`nMCP Tools Results: $successCount/$totalTools successful" -ForegroundColor $(if ($successCount -eq $totalTools) { "Green" } else { "Yellow" })
    return $successCount
}

function Test-AllMCPResources {
    Write-Host "`n=== Testing All 7 MCP Resources ===" -ForegroundColor Cyan
    
    $successCount = 0
    $totalResources = 7
    
    # Resource 1: terrain-types
    Write-Host "1. Testing terrain-types resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://terrain-types" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "   ✓ Success: $($result.terrain_types.Count) terrain types" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Resource 2: environment-types
    Write-Host "2. Testing environment-types resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://environment-types" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "   ✓ Success: $($result.environment_types.Count) environment types" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Resource 3: region-stats
    Write-Host "3. Testing region-stats resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://region-stats" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "   ✓ Success: $($result.total_regions) total regions" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Resource 4: schema
    Write-Host "4. Testing schema resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://schema" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "   ✓ Success: Schema information loaded" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Resource 5: recent-regions
    Write-Host "5. Testing recent-regions resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://recent-regions" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "   ✓ Success: Recent regions loaded" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Resource 6: capabilities
    Write-Host "6. Testing capabilities resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://capabilities" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "   ✓ Success: Capabilities information loaded" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Resource 7: map-overview
    Write-Host "7. Testing map-overview resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://map-overview" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "   ✓ Success: Map overview loaded" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`nMCP Resources Results: $successCount/$totalResources successful" -ForegroundColor $(if ($successCount -eq $totalResources) { "Green" } else { "Yellow" })
    return $successCount
}

function Test-CompleteMCPCapabilities {
    Write-Host "`n=== COMPREHENSIVE MCP TEST SUITE (17 Capabilities) ===" -ForegroundColor Magenta
    
    $toolsSuccess = Test-AllMCPTools
    $resourcesSuccess = Test-AllMCPResources
    
    $totalSuccess = $toolsSuccess + $resourcesSuccess
    $totalCapabilities = 17
    
    Write-Host "`n=== FINAL RESULTS ===" -ForegroundColor Magenta
    Write-Host "Tools: $toolsSuccess/10 successful" -ForegroundColor $(if ($toolsSuccess -eq 10) { "Green" } else { "Yellow" })
    Write-Host "Resources: $resourcesSuccess/7 successful" -ForegroundColor $(if ($resourcesSuccess -eq 7) { "Green" } else { "Yellow" })
    Write-Host "Total MCP Capabilities: $totalSuccess/$totalCapabilities successful" -ForegroundColor $(if ($totalSuccess -eq $totalCapabilities) { "Green" } elseif ($totalSuccess -gt 12) { "Yellow" } else { "Red" })
    
    if ($totalSuccess -eq $totalCapabilities) {
        Write-Host "🎉 All MCP capabilities are working perfectly!" -ForegroundColor Green
    } elseif ($totalSuccess -gt 12) {
        Write-Host "⚠️  Most MCP capabilities working, some issues detected" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Significant MCP issues detected, check deployment" -ForegroundColor Red
    }
    
    return $totalSuccess
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

# Function: Find zone entrances using new endpoint
function Get-ZoneEntrances {
    $entrances = Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/navigation/entrances" -Headers @{"Authorization" = "Bearer $API_KEY"}
    
    Write-Host "Found $($entrances.entrance_count) zone entrances:"
    
    foreach ($entrance in $entrances.entrances | Select-Object -First 10) {
        $room = $entrance.wilderness_room
        Write-Host "Room $($room.vnum): '$($room.name)' at ($($room.x),$($room.y))"
        foreach ($exit in $entrance.zone_exits) {
            Write-Host "  -> $($exit.direction) to Room $($exit.to_room_vnum) (Zone $($exit.to_zone))"
        }
    }
    
    return $entrances
}

# ===========================================
# QUICK TEST SUITE
# ===========================================

function Test-WildernessAPI {
    Write-Host "=== Running Comprehensive Test Suite ===" -ForegroundColor Green
    
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
        $terrain = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0`&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}
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
    
    # Test 4: Zone entrances
    Write-Host "`n4. Testing zone entrances..." -ForegroundColor Yellow
    try {
        $entrances = Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/navigation/entrances" -Headers @{"Authorization" = "Bearer $API_KEY"}
        Write-Host "✓ Found $($entrances.entrance_count) zone entrances" -ForegroundColor Green
    } catch {
        Write-Host "✗ Zone entrances failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 5: MCP Tools (Sample)
    Write-Host "`n5. Testing MCP Tools (sample)..." -ForegroundColor Yellow
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
    
    # Test 6: MCP Resources (Sample)
    Write-Host "`n6. Testing MCP Resources (sample)..." -ForegroundColor Yellow
    try {
        $null = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://terrain-types" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "✓ MCP resource access successful" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP resource access failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 7: MCP zone entrances
    Write-Host "`n7. Testing MCP zone entrances..." -ForegroundColor Yellow
    try {
        $mcpResult = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_zone_entrances" `
            -Method POST `
            -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
            -Body "{}"
        Write-Host "✓ MCP found $($mcpResult.result.entrance_count) zone entrances" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP zone entrances failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`n=== Quick Test Suite Complete ===" -ForegroundColor Green
    Write-Host "For comprehensive testing of all 17 MCP capabilities, scroll up to the detailed test sections!" -ForegroundColor Cyan
}

# ===========================================
# USAGE EXAMPLES
# ===========================================

<#
# Quick start - run the basic test suite
Test-WildernessAPI

# Test all 17 MCP capabilities comprehensively
Test-CompleteMCPCapabilities

# Test only MCP tools (10 tools)
Test-AllMCPTools

# Test only MCP resources (7 resources)
Test-AllMCPResources

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

# Test individual MCP tools
$body = @{ x = 50; y = -25 } | ConvertTo-Json
Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} -Body $body

# Access MCP resources directly
Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://terrain-types" -Headers @{"X-API-Key" = $MCP_API_KEY}
#>

Write-Host "Comprehensive Wilderness and MCP API Test Suite Loaded!" -ForegroundColor Cyan
Write-Host "Environment variables are set:" -ForegroundColor Yellow
Write-Host "  API_KEY: $($API_KEY.Substring(0,8))..." -ForegroundColor Yellow
Write-Host "  BASE_URL: $BASE_URL" -ForegroundColor Yellow
Write-Host "  MCP_API_KEY: $($MCP_API_KEY.Substring(0,8))..." -ForegroundColor Yellow
Write-Host "  MCP_URL: $MCP_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Quick Start Commands:" -ForegroundColor Green
Write-Host "  Test-WildernessAPI                # Basic functionality test" -ForegroundColor White
Write-Host "  Test-CompleteMCPCapabilities      # Test all 17 MCP capabilities" -ForegroundColor White
Write-Host "  Test-AllMCPTools                  # Test 10 MCP tools only" -ForegroundColor White
Write-Host "  Test-AllMCPResources              # Test 7 MCP resources only" -ForegroundColor White
Write-Host ""
Write-Host "📊 Coverage: Backend API + Zone Entrances + 10 MCP Tools + 7 MCP Resources = 17 Total MCP Capabilities" -ForegroundColor Cyan

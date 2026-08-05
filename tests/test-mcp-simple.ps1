# Simple MCP Test Suite
# Environment Variables
$API_KEY = "0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"
$BASE_URL = "http://luminarimud.com:8000"
$MCP_API_KEY = "xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="
$MCP_URL = "http://luminarimud.com:8001"

function Test-BasicAPI {
    Write-Host "=== Basic API Tests ===" -ForegroundColor Green
    
    # Test 1: Health check
    Write-Host "1. API Health Check..." -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "$BASE_URL/api/health"
        Write-Host "✓ API Status: $($health.status)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
        return
    }
    
    # Test 2: Basic terrain
    Write-Host "2. Basic Terrain Query..." -ForegroundColor Yellow
    try {
        $terrain = Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0`&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}
        Write-Host "✓ Terrain at (0,0): $($terrain.data.sector_name)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Terrain query failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 3: Zone entrances
    Write-Host "3. Zone Entrances..." -ForegroundColor Yellow
    try {
        $entrances = Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/navigation/entrances" -Headers @{"Authorization" = "Bearer $API_KEY"}
        Write-Host "✓ Found $($entrances.entrance_count) zone entrances" -ForegroundColor Green
    } catch {
        Write-Host "✗ Zone entrances failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-MCPTools {
    Write-Host "`n=== MCP Tools Tests ===" -ForegroundColor Green
    
    # Tool 1: Terrain analysis
    Write-Host "1. MCP Terrain Analysis..." -ForegroundColor Yellow
    try {
        $body = @{ x = 0; y = 0 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" `
            -Method POST `
            -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
            -Body $body
        Write-Host "✓ MCP Terrain: Success" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP Terrain failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 2: Find room
    Write-Host "2. MCP Find Room..." -ForegroundColor Yellow
    try {
        $body = @{ x = 0; y = 0 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_wilderness_room" `
            -Method POST `
            -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
            -Body $body
        Write-Host "✓ MCP Find Room: Success" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP Find Room failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 3: Zone entrances
    Write-Host "3. MCP Zone Entrances..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_zone_entrances" `
            -Method POST `
            -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
            -Body "{}"
        Write-Host "✓ MCP Zone Entrances: Found $($result.result.entrance_count) entrances" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP Zone Entrances failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Tool 4: Generate map
    Write-Host "4. MCP Generate Map..." -ForegroundColor Yellow
    try {
        $body = @{ center_x = 0; center_y = 0; radius = 5 } | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/generate_wilderness_map" `
            -Method POST `
            -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
            -Body $body
        Write-Host "✓ MCP Map Generation: Success" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP Map Generation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}
}

function Test-MCPResources {
    Write-Host "`n=== MCP Resources Tests ===" -ForegroundColor Green
    
    # Resource 1: Terrain types
    Write-Host "1. MCP Terrain Types Resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://terrain-types" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "✓ MCP Terrain Types: Success" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP Terrain Types failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Resource 2: Capabilities
    Write-Host "2. MCP Capabilities Resource..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$MCP_URL/mcp/resources/wildeditor://capabilities" `
            -Headers @{"X-API-Key" = $MCP_API_KEY}
        Write-Host "✓ MCP Capabilities: Success" -ForegroundColor Green
    } catch {
        Write-Host "✗ MCP Capabilities failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}
}

function Test-All {
    Write-Host "=== Complete MCP Test Suite ===" -ForegroundColor Magenta
    Test-BasicAPI
    Test-MCPTools
    Test-MCPResources
    Write-Host "`n=== All Tests Complete ===" -ForegroundColor Magenta
}

# Auto-load message
Write-Host "Simple MCP Test Suite Loaded!" -ForegroundColor Cyan
Write-Host "Commands available:" -ForegroundColor Yellow
Write-Host "  Test-All           # Run all tests" -ForegroundColor White
Write-Host "  Test-BasicAPI      # Test backend API only" -ForegroundColor White
Write-Host "  Test-MCPTools      # Test MCP tools only" -ForegroundColor White
Write-Host "  Test-MCPResources  # Test MCP resources only" -ForegroundColor White
Write-Host ""
Write-Host "Quick start: Run 'Test-All'" -ForegroundColor Green

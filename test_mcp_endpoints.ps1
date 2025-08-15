# Test MCP Server Endpoints
# Copy and paste these commands to test the MCP server

# Test health check (public)
Invoke-WebRequest -Uri http://localhost:8001/health -UseBasicParsing | ConvertFrom-Json

# Test MCP status (requires auth)
$headers = @{"X-API-Key" = "test-mcp-key"}
Invoke-WebRequest -Uri http://localhost:8001/mcp/status -Headers $headers -UseBasicParsing | ConvertFrom-Json

# List available tools
Invoke-WebRequest -Uri http://localhost:8001/mcp/tools -Headers $headers -UseBasicParsing | ConvertFrom-Json

# List available resources  
Invoke-WebRequest -Uri http://localhost:8001/mcp/resources -Headers $headers -UseBasicParsing | ConvertFrom-Json

# List available prompts
Invoke-WebRequest -Uri http://localhost:8001/mcp/prompts -Headers $headers -UseBasicParsing | ConvertFrom-Json

# Read terrain types resource
Invoke-WebRequest -Uri http://localhost:8001/mcp/resources/terrain-types -Headers $headers -UseBasicParsing | ConvertFrom-Json

# Call analyze_region tool (will show error since backend not running, but demonstrates functionality)
$body = @{region_id = 1} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8001/mcp/tools/analyze_region -Method POST -Headers $headers -Body $body -ContentType "application/json" -UseBasicParsing | ConvertFrom-Json

# Get create_region prompt
$body = @{terrain_type = "forest"; environment = "temperate"} | ConvertTo-Json  
Invoke-WebRequest -Uri http://localhost:8001/mcp/prompts/create_region -Method POST -Headers $headers -Body $body -ContentType "application/json" -UseBasicParsing | ConvertFrom-Json

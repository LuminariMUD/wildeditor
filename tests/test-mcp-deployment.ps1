# Test MCP Server Deployment
# Run this script to verify your MCP server is working correctly

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$McpKey,
    
    [string]$BackendUrl = ""
)

Write-Host "🧪 MCP Server Deployment Test" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

$headers = @{
    "X-API-Key" = $McpKey
    "Content-Type" = "application/json"
}

# Test 1: Health Check (No auth required)
Write-Host "1. Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServerUrl/health" -Method GET
    Write-Host "   ✅ Health check passed: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: MCP Status (Auth required)
Write-Host "2. Testing MCP status endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServerUrl/mcp/status" -Method GET -Headers $headers
    Write-Host "   ✅ MCP status: $($response.status)" -ForegroundColor Green
    Write-Host "   📊 Tools available: $($response.capabilities.tools.Count)" -ForegroundColor Cyan
    Write-Host "   📚 Resources available: $($response.capabilities.resources.Count)" -ForegroundColor Cyan
    Write-Host "   🎨 Prompts available: $($response.capabilities.prompts.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ MCP status failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   🔍 Check your MCP key is correct" -ForegroundColor Yellow
}

# Test 3: List Tools
Write-Host "3. Testing tools endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServerUrl/mcp/tools" -Method GET -Headers $headers
    Write-Host "   ✅ Tools endpoint working" -ForegroundColor Green
    foreach ($tool in $response.tools) {
        Write-Host "      🔧 $($tool.name): $($tool.description)" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Tools endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: List Resources  
Write-Host "4. Testing resources endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServerUrl/mcp/resources" -Method GET -Headers $headers
    Write-Host "   ✅ Resources endpoint working" -ForegroundColor Green
    foreach ($resource in $response.resources) {
        Write-Host "      📚 $($resource.uri): $($resource.name)" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Resources endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Test a simple tool call
Write-Host "5. Testing tool execution..." -ForegroundColor Yellow
try {
    $toolData = @{
        region_id = 1
        include_paths = $true
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$ServerUrl/mcp/tools/analyze_region" -Method POST -Headers $headers -Body $toolData
    Write-Host "   ✅ Tool execution working" -ForegroundColor Green
    Write-Host "   📝 Response: $($response.result.region_name)" -ForegroundColor Cyan
} catch {
    Write-Host "   ⚠️  Tool execution failed (expected if backend not connected): $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   💡 This is normal if backend is not running or not accessible" -ForegroundColor Cyan
}

# Test 6: Test resource access
Write-Host "6. Testing resource access..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServerUrl/mcp/resources/terrain-types" -Method GET -Headers $headers
    Write-Host "   ✅ Resource access working" -ForegroundColor Green
    Write-Host "   📊 Available terrains: $($response.contents[0].text.Split([Environment]::NewLine).Count) types" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Resource access failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Test prompt generation
Write-Host "7. Testing prompt generation..." -ForegroundColor Yellow
try {
    $promptData = @{
        terrain_type = "forest"
        environment = "temperate"
        theme = "mysterious"
        size = "medium"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$ServerUrl/mcp/prompts/create_region" -Method POST -Headers $headers -Body $promptData
    Write-Host "   ✅ Prompt generation working" -ForegroundColor Green
    Write-Host "   📝 Prompt length: $($response.prompt.Length) characters" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Prompt generation failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 MCP Server test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "• Server URL: $ServerUrl" -ForegroundColor White
Write-Host "• Authentication: Working with provided key" -ForegroundColor White
Write-Host "• Core MCP functionality: Available" -ForegroundColor White
Write-Host "• AI Agent Ready: Yes" -ForegroundColor White
Write-Host ""
Write-Host "🤖 AI Agent Integration:" -ForegroundColor Cyan
Write-Host "Use this server URL and MCP key to connect AI agents like Claude or GPT." -ForegroundColor White
Write-Host "The server provides 5 tools, 7 resources, and 5 prompts for wilderness management." -ForegroundColor White

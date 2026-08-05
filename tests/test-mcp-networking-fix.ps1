# PowerShell Test for MCP Networking Fix
# Test MCP → Backend connectivity after docker networking fix

# Configuration
$MCP_URL = "http://luminarimud.com:8001"
$BACKEND_URL = "http://luminarimud.com:8000"
$MCP_API_KEY = $env:WILDEDITOR_MCP_KEY
$BACKEND_API_KEY = ""

if (-not $MCP_API_KEY) {
    throw "WILDEDITOR_MCP_KEY is required"
}

Write-Host "🔍 Testing MCP Docker Networking Fix" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Write-Host "`n1. 🏥 Testing Backend Health..." -ForegroundColor Yellow
try {
    $backendHealth = Invoke-RestMethod -Uri "$BACKEND_URL/api/health" -TimeoutSec 10
    Write-Host "   ✅ Backend is healthy: $($backendHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. 🏥 Testing MCP Health..." -ForegroundColor Yellow
try {
    $mcpHealth = Invoke-RestMethod -Uri "$MCP_URL/health" -TimeoutSec 10
    Write-Host "   ✅ MCP server is healthy" -ForegroundColor Green
} catch {
    Write-Host "   ❌ MCP health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n3. 🔗 Testing MCP → Backend Connectivity..." -ForegroundColor Yellow
Write-Host "   Calling MCP tool that requires backend access..." -ForegroundColor Gray

try {
    $mcpBody = @{
        x = 0
        y = 0
    } | ConvertTo-Json

    $mcpResponse = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" `
        -Method POST `
        -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
        -Body $mcpBody `
        -TimeoutSec 30

    Write-Host "   ✅ MCP successfully connected to backend!" -ForegroundColor Green
    Write-Host "   📄 Response preview:" -ForegroundColor Gray
    if ($mcpResponse.result) {
        Write-Host "      Result: $($mcpResponse.result)" -ForegroundColor Gray
    } elseif ($mcpResponse.data) {
        Write-Host "      Data: $($mcpResponse.data | ConvertTo-Json -Compress)" -ForegroundColor Gray
    } else {
        Write-Host "      $($mcpResponse | ConvertTo-Json -Compress -Depth 2)" -ForegroundColor Gray
    }
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "   ❌ MCP tool call failed (HTTP $statusCode)" -ForegroundColor Red
    Write-Host "   📄 Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        try {
            $errorDetails = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorDetails)
            $errorBody = $reader.ReadToEnd()
            Write-Host "   📄 Response body: $errorBody" -ForegroundColor Red
        } catch {}
    }
}

Write-Host "`n4. 🔍 Additional Connectivity Tests..." -ForegroundColor Yellow

# Test direct backend terrain endpoint
Write-Host "   Testing direct backend terrain endpoint..." -ForegroundColor Gray
try {
    $terrainResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/terrain/at-coordinates?x=0&y=0" `
        -Headers @{"Authorization" = "Bearer $BACKEND_API_KEY"} `
        -TimeoutSec 10
    Write-Host "   ✅ Backend terrain endpoint works" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Backend terrain endpoint issue: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test MCP status endpoint
Write-Host "   Testing MCP status endpoint..." -ForegroundColor Gray
try {
    $mcpStatus = Invoke-RestMethod -Uri "$MCP_URL/mcp/status" `
        -Headers @{"X-API-Key" = $MCP_API_KEY} `
        -TimeoutSec 10
    Write-Host "   ✅ MCP status endpoint works" -ForegroundColor Green
    if ($mcpStatus.backend_url) {
        Write-Host "      Backend URL: $($mcpStatus.backend_url)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  MCP status endpoint issue: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n5. 📊 Summary" -ForegroundColor Yellow
Write-Host "   - Backend: $BACKEND_URL" -ForegroundColor Gray
Write-Host "   - MCP: $MCP_URL" -ForegroundColor Gray
Write-Host "   - Test completed at: $(Get-Date)" -ForegroundColor Gray

Write-Host "`n✅ Networking verification complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 If all tests passed, the networking fix is working!" -ForegroundColor Cyan
Write-Host "🔧 If tests failed, check the deployment logs and container networking." -ForegroundColor Yellow

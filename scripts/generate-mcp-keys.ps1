# Generate API Keys for MCP Server Deployment
# Run this script to generate the required authentication keys

Write-Host "🔑 MCP Server API Key Generator" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Function to generate a secure random base64 key
function Generate-SecureKey {
    param([string]$Purpose)
    
    $bytes = New-Object byte[] 32
    $rng = New-Object Security.Cryptography.RNGCryptoServiceProvider
    $rng.GetBytes($bytes)
    $key = [Convert]::ToBase64String($bytes)
    $rng.Dispose()
    
    Write-Host "✅ $Purpose" -ForegroundColor Green
    Write-Host "   Key: $key" -ForegroundColor Yellow
    Write-Host ""
    
    return $key
}

# Generate MCP keys
Write-Host "Generating authentication key for MCP server deployment..." -ForegroundColor White
Write-Host ""

$mcpKey = Generate-SecureKey "WILDEDITOR_MCP_KEY (for AI agents to access MCP server)"

Write-Host "📋 GitHub Secrets Setup Instructions:" -ForegroundColor Cyan
Write-Host "1. Go to your GitHub repository" -ForegroundColor White
Write-Host "2. Click Settings → Secrets and variables → Actions" -ForegroundColor White
Write-Host "3. Click 'New repository secret'" -ForegroundColor White
Write-Host "4. Add this secret:" -ForegroundColor White
Write-Host ""

Write-Host "Secret Name: WILDEDITOR_MCP_KEY" -ForegroundColor Magenta
Write-Host "Secret Value: $mcpKey" -ForegroundColor Yellow
Write-Host ""

Write-Host "💡 Additional Required Secrets (if not already set):" -ForegroundColor Cyan
Write-Host "• PRODUCTION_HOST - Your server IP or domain" -ForegroundColor White
Write-Host "• PRODUCTION_USER - SSH username (e.g., 'wildedit')" -ForegroundColor White
Write-Host "• PRODUCTION_SSH_KEY - Your SSH private key" -ForegroundColor White
Write-Host "• MYSQL_DATABASE_URL - Your database connection string" -ForegroundColor White
Write-Host "• WILDEDITOR_API_KEY - Your backend API key (also used for MCP-to-backend calls)" -ForegroundColor White
Write-Host ""

Write-Host "🧪 Testing the Key:" -ForegroundColor Cyan
Write-Host "After deployment, test your MCP server with:" -ForegroundColor White
Write-Host "curl -H `"X-API-Key: $mcpKey`" http://your-server:8001/mcp/status" -ForegroundColor Gray
Write-Host ""

Write-Host "🔒 Security Notes:" -ForegroundColor Red
Write-Host "• Keep these keys secure and private" -ForegroundColor White
Write-Host "• Use different keys for development, staging, and production" -ForegroundColor White
Write-Host "• Rotate keys regularly" -ForegroundColor White
Write-Host "• Never commit keys to version control" -ForegroundColor White
Write-Host ""

Write-Host "✅ Key generation complete!" -ForegroundColor Green
Write-Host "Copy the keys above into your GitHub repository secrets." -ForegroundColor White

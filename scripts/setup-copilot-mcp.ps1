# GitHub Copilot MCP Integration Setup
# This script helps configure GitHub Copilot to work with the Wildeditor MCP server

param(
    [string]$McpKey = "",
    [string]$ApiKey = "",
    [switch]$Help
)

if ($Help) {
    Write-Host @"
GitHub Copilot MCP Setup for Wildeditor

USAGE:
    .\scripts\setup-copilot-mcp.ps1 -McpKey "your-mcp-key" -ApiKey "your-api-key"

DESCRIPTION:
    This script configures GitHub Copilot in VS Code to use the Wildeditor MCP server
    running at luminarimud.com:8001. The MCP server provides AI-powered tools for
    wilderness management including terrain analysis, landmark creation, and path generation.

PARAMETERS:
    -McpKey     The MCP operations key (WILDEDITOR_MCP_KEY)
    -ApiKey     The backend API key (WILDEDITOR_API_KEY)
    -Help       Show this help message

EXAMPLE:
    .\scripts\setup-copilot-mcp.ps1 -McpKey "mcp_12345..." -ApiKey "api_67890..."

"@
    return
}

Write-Host "🚀 Setting up GitHub Copilot MCP Integration for Wildeditor" -ForegroundColor Cyan
Write-Host ""

# Check if VS Code is installed
$vscodePath = Get-Command code -ErrorAction SilentlyContinue
if (-not $vscodePath) {
    Write-Host "❌ VS Code not found in PATH. Please install VS Code first." -ForegroundColor Red
    return
}

# Check if required parameters are provided
if (-not $McpKey -or -not $ApiKey) {
    Write-Host "⚠️  MCP Key and API Key are required." -ForegroundColor Yellow
    Write-Host "Get your keys from the project documentation or ask the project maintainer."
    Write-Host ""
    Write-Host "Usage: .\scripts\setup-copilot-mcp.ps1 -McpKey 'your-mcp-key' -ApiKey 'your-api-key'"
    return
}

Write-Host "🔧 Configuring environment variables..." -ForegroundColor Green

# Set user environment variables
[Environment]::SetEnvironmentVariable("WILDEDITOR_MCP_KEY", $McpKey, "User")
[Environment]::SetEnvironmentVariable("WILDEDITOR_API_KEY", $ApiKey, "User")
[Environment]::SetEnvironmentVariable("WILDEDITOR_MCP_SERVER_URL", "http://luminarimud.com:8001", "User")
[Environment]::SetEnvironmentVariable("WILDEDITOR_BACKEND_URL", "http://luminarimud.com:8000", "User")

Write-Host "✅ Environment variables set" -ForegroundColor Green

# Test MCP server connectivity
Write-Host "🌐 Testing MCP server connectivity..." -ForegroundColor Green

try {
    $response = Invoke-WebRequest -Uri "http://luminarimud.com:8001/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ MCP server is accessible" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MCP server responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Cannot reach MCP server: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   The server might be down or firewall may be blocking the connection." -ForegroundColor Yellow
}

# Install GitHub Copilot extensions if not already installed
Write-Host "📦 Checking GitHub Copilot extensions..." -ForegroundColor Green

$extensions = & code --list-extensions
$copilotInstalled = $extensions -contains "GitHub.copilot"
$copilotChatInstalled = $extensions -contains "GitHub.copilot-chat"

if (-not $copilotInstalled) {
    Write-Host "📥 Installing GitHub Copilot extension..." -ForegroundColor Yellow
    & code --install-extension GitHub.copilot
} else {
    Write-Host "✅ GitHub Copilot extension already installed" -ForegroundColor Green
}

if (-not $copilotChatInstalled) {
    Write-Host "📥 Installing GitHub Copilot Chat extension..." -ForegroundColor Yellow
    & code --install-extension GitHub.copilot-chat
} else {
    Write-Host "✅ GitHub Copilot Chat extension already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor White
Write-Host "1. Restart VS Code to load the new environment variables" -ForegroundColor White
Write-Host "2. Open a file in the wildeditor workspace" -ForegroundColor White
Write-Host "3. Start GitHub Copilot Chat and try these commands:" -ForegroundColor White
Write-Host "   - 'Analyze the wilderness region structure'" -ForegroundColor Gray
Write-Host "   - 'How do I create a new landmark?'" -ForegroundColor Gray
Write-Host "   - 'Generate a path between two regions'" -ForegroundColor Gray
Write-Host ""
Write-Host "MCP SERVER TOOLS AVAILABLE:" -ForegroundColor White
Write-Host "• analyze_region - Analyze terrain and features" -ForegroundColor Gray
Write-Host "• create_landmarks - Create landmarks in regions" -ForegroundColor Gray
Write-Host "• generate_paths - Generate wilderness paths" -ForegroundColor Gray
Write-Host "• region_summary - Get comprehensive region info" -ForegroundColor Gray
Write-Host ""
Write-Host "For troubleshooting, check the VS Code output panel and ensure" -ForegroundColor Yellow
Write-Host "your GitHub Copilot subscription is active." -ForegroundColor Yellow

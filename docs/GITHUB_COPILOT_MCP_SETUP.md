# GitHub Copilot + Wildeditor MCP Integration Guide

## 🎯 Overview

This guide explains how to configure GitHub Copilot in VS Code to use the Wildeditor MCP (Model Context Protocol) server for enhanced AI-powered wilderness management capabilities.

## 🏗️ Architecture

```
VS Code + GitHub Copilot
    ↓
Wildeditor MCP Server (luminarimud.com:8001)
    ↓
Wildeditor Backend API (luminarimud.com:8000)
    ↓
MySQL Database
```

## 🚀 Quick Setup

### 1. Run the Setup Script

```powershell
.\setup-copilot-mcp.ps1 -McpKey "your-mcp-key" -ApiKey "your-api-key"
```

### 2. Restart VS Code

After running the setup script, restart VS Code to load the new environment variables.

### 3. Verify Installation

1. Open VS Code in the wildeditor workspace
2. Open GitHub Copilot Chat (Ctrl+Shift+I)
3. Try asking: "What wilderness management tools are available?"

## 🔧 Manual Configuration

If you prefer to configure manually:

### Environment Variables

Add these to your system environment variables:

```bash
WILDEDITOR_MCP_KEY=your-mcp-operations-key
WILDEDITOR_API_KEY=your-backend-api-key
WILDEDITOR_MCP_SERVER_URL=http://luminarimud.com:8001
WILDEDITOR_BACKEND_URL=http://luminarimud.com:8000
```

### VS Code Extensions

Install these extensions:
- `GitHub.copilot`
- `GitHub.copilot-chat`

### VS Code Settings

The workspace already includes optimized settings in `.vscode/settings.json`.

## 🛠️ Available MCP Tools

When GitHub Copilot is properly configured, it can access these wilderness management tools:

### `analyze_region`
- **Purpose**: Analyze terrain features, elevation patterns, and natural landmarks
- **Example**: "Analyze the terrain complexity of region 5"

### `create_landmarks`
- **Purpose**: Create and place landmarks within wilderness regions
- **Example**: "Create a mountain peak landmark in the northern section"

### `generate_paths`
- **Purpose**: Generate optimized paths between locations
- **Example**: "Create a path from the forest entrance to the mountain base"

### `region_summary`
- **Purpose**: Get comprehensive information about regions
- **Example**: "Summarize all features and paths in region 3"

## 💬 Using GitHub Copilot Chat

### Example Conversations

**Terrain Analysis:**
```
You: "Analyze the wilderness region with ID 1"
Copilot: [Uses analyze_region tool to provide detailed terrain analysis]
```

**Path Planning:**
```
You: "I need to connect the eastern forest to the western mountains"
Copilot: [Uses generate_paths tool to create optimal routes]
```

**Landmark Creation:**
```
You: "Add a waterfall landmark near coordinates (100, 150)"
Copilot: [Uses create_landmarks tool to place the feature]
```

### Code Assistance

GitHub Copilot can also help with:
- **Backend Development**: Understanding API endpoints and database models
- **Frontend Development**: React components for wilderness visualization
- **Database Queries**: SQL for region and path management
- **Authentication**: API key handling and middleware

## 🔍 Troubleshooting

### Common Issues

#### 1. MCP Server Not Accessible
```bash
# Test connectivity
Test-NetConnection luminarimud.com -Port 8001
```

#### 2. Environment Variables Not Set
```powershell
# Check if variables are set
echo $env:WILDEDITOR_MCP_KEY
echo $env:WILDEDITOR_API_KEY
```

#### 3. GitHub Copilot Not Responding
- Ensure GitHub Copilot subscription is active
- Check VS Code output panel for error messages
- Restart VS Code after environment changes

#### 4. Authentication Errors
- Verify your MCP key is correct
- Check that the key has proper permissions
- Ensure the backend API key matches

### Health Checks

Test the MCP server directly:

```powershell
# Basic health check
Invoke-WebRequest -Uri "http://luminarimud.com:8001/health"

# Authenticated health check (requires MCP key)
$headers = @{"X-API-Key" = "your-mcp-key"}
Invoke-WebRequest -Uri "http://luminarimud.com:8001/health" -Headers $headers
```

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use system environment variables for keys
- **Network Security**: MCP server uses API key authentication
- **Firewall**: Ensure port 8001 is accessible if needed

## 📊 Monitoring

Monitor MCP server usage:
- **Health Endpoint**: `http://luminarimud.com:8001/health`
- **Logs**: Check server logs for API usage
- **Performance**: Monitor response times for AI operations

## 🎓 Best Practices

### For AI Conversations
1. **Be Specific**: "Analyze region 5's terrain" vs "Look at the map"
2. **Use Context**: Reference specific regions, coordinates, or features
3. **Iterate**: Build on previous responses for complex tasks

### For Development
1. **Code Context**: Keep relevant files open for better AI assistance
2. **Documentation**: Reference project docs for architectural decisions
3. **Testing**: Use AI to help write and debug tests

## 📚 Additional Resources

- **MCP Server Documentation**: `apps/mcp/README.md`
- **API Documentation**: `docs/backend/API.md`
- **Architecture Guide**: `docs/mcp/ARCHITECTURE.md`
- **Development Setup**: `docs/mcp/DEVELOPMENT_SETUP.md`

## 🆘 Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review MCP server logs
3. Test individual API endpoints
4. Consult the project documentation
5. Ask the development team

---

**Note**: This integration requires an active GitHub Copilot subscription and proper authentication keys for the Wildeditor MCP server.

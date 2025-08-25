# GitHub Actions Secrets to Add

## Quick Setup Instructions

1. Go to: https://github.com/LuminariMUD/wildeditor/settings/secrets/actions
2. Click "New repository secret" for each secret below
3. Copy the exact values provided

## Required Secrets

### Authentication Keys (Generate New)
Generate these using the command: `openssl rand -base64 32`

| Secret Name | Value |
|------------|-------|
| `WILDEDITOR_MCP_KEY` | *(Generate new 32-byte key)* |
| `WILDEDITOR_API_KEY` | *(Generate new 32-byte key)* |

### Production Server
| Secret Name | Value |
|------------|-------|
| `PRODUCTION_HOST` | `luminarimud.com` |
| `PRODUCTION_USER` | `root` |
| `PRODUCTION_SSH_KEY` | *(Your SSH private key for server access)* |

### OpenAI Configuration
| Secret Name | Value |
|------------|-------|
| `AI_PROVIDER` | `openai` |
| `OPENAI_API_KEY` | *(Copy from ~/Luminari-Source/lib/.env line 92)* |
| `OPENAI_MODEL` | `gpt-4o-mini` |

## How the System Works

1. **GitHub Actions Workflow** reads these secrets during deployment
2. **Docker Container** receives them as environment variables:
   ```bash
   -e WILDEDITOR_MCP_KEY="$MCP_KEY"
   -e WILDEDITOR_API_KEY="$MCP_BACKEND_KEY"
   -e AI_PROVIDER="${AI_PROVIDER:-none}"
   -e OPENAI_API_KEY="$OPENAI_API_KEY"
   -e OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}"
   ```
3. **MCP Server** in the container uses these environment variables automatically
4. **AI Service** detects OpenAI is configured and enables AI generation

## After Adding Secrets

1. **Trigger Deployment**: Push any change to main branch
2. **Monitor**: Check GitHub Actions tab for deployment status
3. **Verify**: The deployment notification will show:
   - AI Provider: openai
   - Tools: 14 Wilderness Management Tools (5 with AI)

## Security Notes

- The API keys are never exposed in logs or code
- They're only available inside the Docker container at runtime
- The workflow file doesn't contain any actual keys
- GitHub encrypts all secrets at rest

## Testing After Deployment

Once deployed, test the AI integration:

```bash
# Test MCP server status
curl -H "X-API-Key: YOUR_MCP_KEY" \
  http://luminarimud.com:8001/mcp/status

# Test AI generation
curl -X POST http://luminarimud.com:8001/mcp/request \
  -H "X-API-Key: YOUR_MCP_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "method": "tools/call",
    "params": {
      "name": "generate_region_description",
      "arguments": {
        "region_name": "Test Valley",
        "terrain_theme": "peaceful valley",
        "description_style": "poetic",
        "description_length": "brief"
      }
    }
  }'
```

## Cost Information

With `gpt-4o-mini`:
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Estimated monthly cost: $5-20 for moderate usage

## Summary

Total secrets to add: **8**
- 5 for deployment and authentication
- 3 for OpenAI integration

The workflow is already configured to use these secrets, so once you add them, the next deployment will automatically have AI-powered description generation enabled!
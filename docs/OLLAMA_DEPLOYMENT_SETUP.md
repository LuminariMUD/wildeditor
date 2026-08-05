# Ollama Integration Deployment Setup

## GitHub Secrets Configuration

To enable the Ollama fallback integration in production, you need to add the following GitHub Secrets:

### Required Secrets for Ollama

1. **Go to GitHub Repository Settings**:
   - Navigate to: https://github.com/LuminariMUD/wildeditor/settings/secrets/actions

2. **Add the following secrets**:

   | Secret Name | Value | Description |
   |------------|-------|-------------|
   | `OLLAMA_BASE_URL` | `http://localhost:11434` | URL of the Ollama service on the production server |
   | `OLLAMA_MODEL` | `llama3.2:1b` | Model to use (matching Luminari-Source configuration) |
   | `AI_PROVIDER` | `openai` | Primary AI provider (keep as OpenAI) |

### Existing Secrets (if not already set)

Make sure these are also configured:
- `OPENAI_API_KEY` - Your OpenAI API key (primary provider)
- `OPENAI_MODEL` - `gpt-4o-mini` (or your preferred model)

## Deployment Process

Once the secrets are configured:

1. **Trigger Deployment**:
   The deployment will automatically trigger when changes are pushed to the `main` branch affecting:
   - `apps/mcp/**`
   - `.github/workflows/mcp-deploy.yml`

2. **Manual Trigger** (if needed):
   - Go to Actions tab
   - Select "MCP Server CI/CD Pipeline"
   - Click "Run workflow"

## Verification

After deployment, verify the Ollama integration:

```bash
# Check MCP health
curl http://luminarimud.com:8001/health

# Test description generation (will use fallback chain)
curl -X POST http://luminarimud.com:8001/mcp \
  -H "X-API-Key: YOUR_MCP_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-description",
    "method": "tools/call",
    "params": {
      "name": "generate_region_description",
      "arguments": {
        "region_name": "Test Region",
        "terrain_theme": "forest",
        "description_style": "poetic",
        "description_length": "brief"
      }
    }
  }'
```

## Expected Behavior

With proper configuration:

1. **Primary (OpenAI)**: If OpenAI API key is valid and service available
   - Response will include: `"ai_provider": "openai"`

2. **Fallback (Ollama)**: If OpenAI fails or is unavailable
   - Response will include: `"ai_provider": "ollama_fallback"`

3. **Final Fallback (Template)**: If both OpenAI and Ollama fail
   - Response will include: `"ai_provider": "template"`

## Troubleshooting

### Check Container Logs
```bash
ssh user@luminarimud.com
docker logs wildeditor-mcp --tail 50
```

### Verify Environment Variables
```bash
docker exec wildeditor-mcp env | grep -E "OLLAMA|AI_PROVIDER|OPENAI"
```

### Test Ollama Directly on Server
```bash
curl http://localhost:11434/api/tags
# Should show llama3.2:1b model
```

## Notes

- The Ollama service must be running on the production server at `localhost:11434`
- The `llama3.2:1b` model must be installed (`ollama pull llama3.2:1b`)
- The fallback chain ensures description generation always works, even without API keys
- Ollama provides local, private AI generation without external API dependencies
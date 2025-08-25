# GitHub Actions Secrets Configuration Guide

This guide explains how to configure GitHub Actions secrets for the Wildeditor MCP server deployment, including AI provider API keys.

## Required Secrets

### Core Authentication Secrets (Required)

These secrets are essential for the MCP server to function:

| Secret Name | Description | How to Generate | Required |
|------------|-------------|-----------------|----------|
| `WILDEDITOR_MCP_KEY` | Authentication key for MCP operations | See generation command below | ✅ Yes |
| `WILDEDITOR_API_KEY` | Backend API authentication key | See generation command below | ✅ Yes |
| `PRODUCTION_HOST` | Production server hostname/IP | Your server's public IP or domain | ✅ Yes |
| `PRODUCTION_USER` | SSH username for deployment | Your server username | ✅ Yes |
| `PRODUCTION_SSH_KEY` | Private SSH key for deployment | Generate SSH keypair | ✅ Yes |

### AI Provider Secrets (Optional)

These secrets enable AI-powered description generation. Configure at least one provider for AI features:

| Secret Name | Description | Default Value | Required |
|------------|-------------|---------------|----------|
| `AI_PROVIDER` | Which AI provider to use | `none` (template fallback) | ❌ No |
| `OPENAI_API_KEY` | OpenAI API key for GPT models | - | ❌ No* |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4-turbo-preview` | ❌ No |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | - | ❌ No* |
| `ANTHROPIC_MODEL` | Anthropic model to use | `claude-3-opus-20240229` | ❌ No |
| `OLLAMA_BASE_URL` | Ollama server URL for local LLMs | - | ❌ No* |
| `OLLAMA_MODEL` | Ollama model to use | `llama2` | ❌ No |

*At least one API key is required if `AI_PROVIDER` is not set to `none`

## How to Add Secrets

### Step 1: Navigate to Repository Settings

1. Go to your GitHub repository: `https://github.com/LuminariMUD/wildeditor`
2. Click on **Settings** tab
3. In the left sidebar, under **Security**, click **Secrets and variables** → **Actions**

### Step 2: Add Required Secrets

Click **New repository secret** for each secret:

#### Generate Authentication Keys

For `WILDEDITOR_MCP_KEY` and `WILDEDITOR_API_KEY`, generate secure random keys:

**On Linux/Mac:**
```bash
openssl rand -base64 32
```

**On Windows PowerShell:**
```powershell
$bytes = New-Object byte[] 32
(New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

**Using Python:**
```python
import secrets
import base64
key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
print(key)
```

#### Add Production Server Details

1. `PRODUCTION_HOST`: Your server's IP address or domain name (e.g., `luminarimud.com`)
2. `PRODUCTION_USER`: SSH username (e.g., `root` or `deploy`)

#### Generate SSH Deployment Key

1. Generate a new SSH key pair (on your local machine):
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-deploy" -f deploy_key
   ```

2. Add the **private key** (`deploy_key`) content as `PRODUCTION_SSH_KEY` secret

3. Add the **public key** (`deploy_key.pub`) to your server:
   ```bash
   ssh-copy-id -i deploy_key.pub user@your-server
   # Or manually add to ~/.ssh/authorized_keys on the server
   ```

### Step 3: Configure AI Provider (Optional)

Choose one or more AI providers:

#### Option A: OpenAI (Recommended for Quality)

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add secrets:
   - `AI_PROVIDER`: `openai`
   - `OPENAI_API_KEY`: Your API key
   - `OPENAI_MODEL`: `gpt-4-turbo-preview` (or `gpt-3.5-turbo` for lower cost)

#### Option B: Anthropic Claude

1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Add secrets:
   - `AI_PROVIDER`: `anthropic`
   - `ANTHROPIC_API_KEY`: Your API key
   - `ANTHROPIC_MODEL`: `claude-3-opus-20240229` (or `claude-3-haiku-20240307` for lower cost)

#### Option C: Ollama (Self-Hosted)

1. Install Ollama on your server or a dedicated machine
2. Add secrets:
   - `AI_PROVIDER`: `ollama`
   - `OLLAMA_BASE_URL`: `http://your-ollama-server:11434`
   - `OLLAMA_MODEL`: `llama2` (or any installed model)

#### Option D: Auto-Detection

Don't set `AI_PROVIDER` - the system will automatically detect available API keys in this order:
1. OpenAI (if `OPENAI_API_KEY` is set)
2. Anthropic (if `ANTHROPIC_API_KEY` is set)
3. Ollama (if `OLLAMA_BASE_URL` is set)
4. Template fallback (if no keys are set)

## Complete Configuration Example

Here's what your secrets should look like in GitHub:

```
Repository Secrets:
├── WILDEDITOR_MCP_KEY        = "xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="
├── WILDEDITOR_API_KEY        = "Hy7kPl9Nx2Qm4RtVwXyZ1aBcDeFgHiJkLmNoPqRsTu0="
├── PRODUCTION_HOST           = "luminarimud.com"
├── PRODUCTION_USER           = "root"
├── PRODUCTION_SSH_KEY        = "-----BEGIN OPENSSH PRIVATE KEY-----..."
├── AI_PROVIDER               = "openai"
├── OPENAI_API_KEY            = "sk-proj-..."
└── OPENAI_MODEL              = "gpt-4-turbo-preview"
```

## Testing Your Configuration

After adding all secrets:

1. **Trigger a deployment** by pushing to the `main` branch:
   ```bash
   git commit --allow-empty -m "Test MCP deployment with AI secrets"
   git push origin main
   ```

2. **Monitor the deployment** in the Actions tab

3. **Check AI provider status** after deployment:
   ```bash
   curl -H "X-API-Key: YOUR_MCP_KEY" \
     http://your-server:8001/mcp/status
   ```

4. **Test AI generation**:
   ```bash
   curl -X POST http://your-server:8001/mcp/request \
     -H "X-API-Key: YOUR_MCP_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "test-1",
       "method": "tools/call",
       "params": {
         "name": "generate_region_description",
         "arguments": {
           "region_name": "Test Region",
           "terrain_theme": "forest"
         }
       }
     }'
   ```

## Security Best Practices

### DO:
- ✅ Use strong, randomly generated keys
- ✅ Rotate keys periodically (every 3-6 months)
- ✅ Use different keys for development and production
- ✅ Limit API key permissions when possible
- ✅ Monitor API usage for anomalies

### DON'T:
- ❌ Commit secrets to the repository
- ❌ Share secrets in issues or pull requests
- ❌ Use the same key across multiple services
- ❌ Log or display full API keys in deployment output

## Cost Management

### Development Phase
Use higher-quality models during initial world-building:
- OpenAI: `gpt-4-turbo-preview` (~$10/1M tokens)
- Anthropic: `claude-3-opus-20240229` (~$15/1M tokens)

### Production Phase
Switch to cost-effective models once established:
- OpenAI: `gpt-3.5-turbo` (~$0.50/1M tokens)
- Anthropic: `claude-3-haiku-20240307` (~$0.25/1M tokens)
- Ollama: Free (self-hosted)

### Monitoring Costs
- Set up usage alerts in your AI provider dashboard
- Use `AI_PROVIDER=none` to disable AI and use templates only
- Monitor the logs for token usage statistics

## Troubleshooting

### Secret Not Found
```
❌ WILDEDITOR_MCP_KEY secret is not set in GitHub repository
```
**Solution**: Ensure the secret name matches exactly (case-sensitive)

### AI Provider Not Working
Check deployment logs for:
```
AI Service initialized with provider: none
```
**Solution**: Verify API keys are correctly set and valid

### SSH Connection Failed
```
❌ SSH connection failed
```
**Solution**: 
1. Verify `PRODUCTION_SSH_KEY` contains the complete private key
2. Ensure public key is in server's `~/.ssh/authorized_keys`
3. Check `PRODUCTION_HOST` and `PRODUCTION_USER` are correct

### Container Not Starting
Check if all required environment variables are passed:
```bash
ssh user@server "docker logs wildeditor-mcp"
```

## Support

For issues with secrets configuration:
1. Check the [Actions tab](https://github.com/LuminariMUD/wildeditor/actions) for deployment logs
2. Review this documentation
3. Contact the development team with deployment run ID

## Appendix: Environment Variable Reference

All environment variables available in the MCP container:

| Variable | Description | Source |
|----------|-------------|--------|
| `WILDEDITOR_MCP_KEY` | MCP authentication key | GitHub Secret |
| `WILDEDITOR_API_KEY` | Backend API key | GitHub Secret |
| `WILDEDITOR_BACKEND_URL` | Backend API URL | Hardcoded: `http://localhost:8000` |
| `ENVIRONMENT` | Deployment environment | Hardcoded: `production` |
| `DEBUG` | Debug mode | Hardcoded: `false` |
| `PORT` | MCP server port | Hardcoded: `8001` |
| `LOG_LEVEL` | Logging level | Hardcoded: `INFO` |
| `AI_PROVIDER` | AI provider selection | GitHub Secret |
| `OPENAI_API_KEY` | OpenAI API key | GitHub Secret |
| `OPENAI_MODEL` | OpenAI model | GitHub Secret |
| `ANTHROPIC_API_KEY` | Anthropic API key | GitHub Secret |
| `ANTHROPIC_MODEL` | Anthropic model | GitHub Secret |
| `OLLAMA_BASE_URL` | Ollama server URL | GitHub Secret |
| `OLLAMA_MODEL` | Ollama model | GitHub Secret |
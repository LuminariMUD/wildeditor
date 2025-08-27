# GitHub Secrets Required for Chat Agent Deployment

## 🔴 Required Secrets

Add these to GitHub → Settings → Secrets and variables → Actions:

### Server Access (Should already be configured for backend/MCP)
```yaml
PRODUCTION_HOST: luminarimud.com    # Your server hostname/IP
PRODUCTION_USER: luminari            # SSH username  
PRODUCTION_SSH_KEY: |                # SSH private key (entire contents)
  -----BEGIN OPENSSH PRIVATE KEY-----
  ...your key here...
  -----END OPENSSH PRIVATE KEY-----
```

### AI Model (Reuses existing secrets from MCP deployment)

#### Primary: OpenAI (if configured)
```yaml
OPENAI_API_KEY: sk-proj-xxxxxxxxxxxxx    # Already set for MCP
OPENAI_MODEL: gpt-4-turbo                # Already set for MCP
```

#### Fallback: DeepSeek (if configured)
```yaml
DEEPSEEK_API_KEY: sk-xxxxxxxxxxxxxxx     # Already set for MCP
DEEPSEEK_MODEL: deepseek-chat            # Already set for MCP
```

#### Optional: Set explicit provider
```yaml
AI_PROVIDER: openai                      # or deepseek (auto-detect if not set)
```

### Integration Keys (Reuses existing secrets)
```yaml
WILDEDITOR_MCP_KEY: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=  # Already set for MCP
WILDEDITOR_API_KEY: 0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu               # Already set for backend
```

## 🟡 Optional Secrets

```yaml
FRONTEND_URL: https://wildedit.luminarimud.com  # Default shown
LOG_LEVEL: INFO                                  # DEBUG, INFO, WARNING, ERROR
SESSION_TTL: 86400                               # Session timeout in seconds
```

## ✅ Summary of Required Secrets

These secrets should already be configured from MCP and backend deployments:

```yaml
# Server Access
PRODUCTION_HOST       # Server hostname
PRODUCTION_USER       # SSH username
PRODUCTION_SSH_KEY    # SSH private key

# AI Provider (at least one required)
OPENAI_API_KEY        # OpenAI API key
DEEPSEEK_API_KEY      # DeepSeek API key (fallback)

# Integration Keys
WILDEDITOR_MCP_KEY    # MCP server API key
WILDEDITOR_API_KEY    # Backend API key

# Optional
AI_PROVIDER           # Force specific provider
OPENAI_MODEL          # OpenAI model name
DEEPSEEK_MODEL        # DeepSeek model name
```

## 📍 Checking Existing Secrets

To verify these secrets are already configured:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. You should see:
   - `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_SSH_KEY`
   - `OPENAI_API_KEY` and/or `DEEPSEEK_API_KEY`
   - `WILDEDITOR_MCP_KEY`, `WILDEDITOR_API_KEY`

If any are missing, check the MCP or backend deployment documentation for setup instructions.

### OpenAI Key
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy key (starts with `sk-`)

### Anthropic Key
1. Go to https://console.anthropic.com/account/keys
2. Create key
3. Copy key

## 🚀 Deploy

After adding all secrets:
1. Push any change to `apps/agent/` folder, OR
2. Go to Actions → "Deploy Chat Agent" → Run workflow

## ❓ Verify Deployment

```bash
# SSH to server and check
ssh user@server
docker ps | grep chat-agent
curl http://localhost:8002/health/
```
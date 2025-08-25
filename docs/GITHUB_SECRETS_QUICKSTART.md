# GitHub Secrets Quick Setup

## 🚀 Quick Start (5 Minutes)

### Step 1: Generate Keys
```bash
# Generate two authentication keys
openssl rand -base64 32  # Copy for WILDEDITOR_MCP_KEY
openssl rand -base64 32  # Copy for WILDEDITOR_API_KEY
```

### Step 2: Add to GitHub
1. Go to: **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:

| Secret | Value |
|--------|-------|
| `WILDEDITOR_MCP_KEY` | *Your generated key 1* |
| `WILDEDITOR_API_KEY` | *Your generated key 2* |
| `PRODUCTION_HOST` | *Your server IP/domain* |
| `PRODUCTION_USER` | *Your SSH username* |
| `PRODUCTION_SSH_KEY` | *Your SSH private key* |

### Step 3: Choose AI Provider (Optional)

#### Option A: OpenAI (Recommended)
| Secret | Value |
|--------|-------|
| `OPENAI_API_KEY` | *Your OpenAI API key* |
| `AI_PROVIDER` | `openai` |

#### Option B: Anthropic
| Secret | Value |
|--------|-------|
| `ANTHROPIC_API_KEY` | *Your Anthropic API key* |
| `AI_PROVIDER` | `anthropic` |

#### Option C: No AI (Template Only)
*Don't add any AI secrets - templates will be used*

### Step 4: Deploy
```bash
git push origin main
```

## 📋 Complete Secrets Checklist

### Required (5 secrets)
- [ ] `WILDEDITOR_MCP_KEY` - Random 32-byte key
- [ ] `WILDEDITOR_API_KEY` - Random 32-byte key  
- [ ] `PRODUCTION_HOST` - Server IP/domain
- [ ] `PRODUCTION_USER` - SSH username
- [ ] `PRODUCTION_SSH_KEY` - SSH private key

### Optional AI (Choose one set)
**OpenAI:**
- [ ] `OPENAI_API_KEY` - From platform.openai.com
- [ ] `AI_PROVIDER` - Set to `openai`
- [ ] `OPENAI_MODEL` - (Optional) Default: `gpt-4-turbo-preview`

**Anthropic:**
- [ ] `ANTHROPIC_API_KEY` - From console.anthropic.com
- [ ] `AI_PROVIDER` - Set to `anthropic`
- [ ] `ANTHROPIC_MODEL` - (Optional) Default: `claude-3-opus-20240229`

**Ollama (Self-hosted):**
- [ ] `OLLAMA_BASE_URL` - Your Ollama server URL
- [ ] `AI_PROVIDER` - Set to `ollama`
- [ ] `OLLAMA_MODEL` - (Optional) Default: `llama2`

## 🔍 Verify Deployment

After pushing to main, check:

1. **GitHub Actions**: Green checkmark ✅
2. **Test MCP Health**:
   ```bash
   curl http://YOUR_SERVER:8001/health
   ```
3. **Test AI Status**:
   ```bash
   curl -H "X-API-Key: YOUR_MCP_KEY" \
     http://YOUR_SERVER:8001/mcp/status
   ```

## 💰 Cost Estimates

| Provider | Model | Cost/1M tokens | Monthly estimate* |
|----------|-------|----------------|-------------------|
| OpenAI | GPT-4 Turbo | ~$10 | $50-200 |
| OpenAI | GPT-3.5 Turbo | ~$0.50 | $5-20 |
| Anthropic | Claude 3 Opus | ~$15 | $75-300 |
| Anthropic | Claude 3 Haiku | ~$0.25 | $2-10 |
| Ollama | Any | $0 | $0 (self-hosted) |

*Based on moderate usage (5-20M tokens/month)

## 🆘 Troubleshooting

### "Secret not found"
→ Check exact spelling (case-sensitive)

### "AI provider: none"
→ Verify API key is valid and AI_PROVIDER is set

### "SSH connection failed"
→ Add public key to server's `~/.ssh/authorized_keys`

### "Port 8001 already in use"
→ Stop existing container: `docker stop wildeditor-mcp`

## 📚 Full Documentation
See [GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md) for detailed instructions.
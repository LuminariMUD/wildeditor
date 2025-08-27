# Chat Agent Deployment Guide

This guide covers the GitHub Actions secrets and deployment configuration needed to deploy the Chat Agent service to production.

## 📋 Prerequisites

1. **VPS Access**: SSH access to the production server
2. **GitHub Repository**: Admin access to add secrets
3. **AI API Key**: Either OpenAI or Anthropic API key
4. **Docker**: Installed on the production server
5. **Network**: `wildeditor-network` Docker network created on server

## 🔐 Required GitHub Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions, then add the following secrets:

### 1. Server Connection Secrets (Should already be configured)

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `PRODUCTION_HOST` | Production server hostname/IP | `luminarimud.com` or `123.45.67.89` |
| `PRODUCTION_USER` | SSH username for deployment | `luminari` |
| `PRODUCTION_SSH_KEY` | SSH private key for authentication | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

**How to get SSH key:**
```bash
# On your local machine, if you have SSH access:
cat ~/.ssh/id_rsa  # or your key file
# Copy the entire contents including BEGIN/END lines
```

### 2. AI Model Configuration (Reuses existing secrets)

The chat agent will use the same AI configuration as the MCP server:

#### Primary Provider: OpenAI (if configured)
| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-abc123...` |
| `OPENAI_MODEL` | Model to use | `gpt-4-turbo` or `gpt-4o` |

**How to get OpenAI API key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

#### Fallback Provider: DeepSeek (cost-effective alternative)
| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | `sk-abc123...` |
| `DEEPSEEK_MODEL` | Model to use | `deepseek-chat` |

#### Optional: Force specific provider
| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AI_PROVIDER` | Force specific provider | `openai` or `deepseek` |

**How to get Anthropic API key:**
1. Go to https://console.anthropic.com/account/keys
2. Click "Create Key"
3. Copy the key

### 3. Service Integration Secrets (Already configured)

| Secret Name | Description | Example Value | Notes |
|------------|-------------|---------------|-------|
| `WILDEDITOR_MCP_KEY` | API key for MCP server | `xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=` | Already set for MCP deployment |
| `WILDEDITOR_API_KEY` | API key for backend | `0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu` | Already set for backend deployment |

**How to find existing API keys:**
```bash
# SSH into production server
ssh user@luminarimud.com

# Check MCP configuration
cat /home/luminari/wildeditor/apps/mcp/.env | grep MCP_API_KEY

# Check backend configuration  
cat /home/luminari/wildeditor/apps/backend/.env | grep API_KEY
```

### 4. Optional Configuration Secrets

| Secret Name | Description | Default Value | Options |
|------------|-------------|---------------|---------|
| `FRONTEND_URL` | Frontend URL for CORS | `https://wildedit.luminarimud.com` | Your frontend URL |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `SESSION_TTL` | Session timeout (seconds) | `86400` (24 hours) | Any positive integer |

## 🚀 Step-by-Step Deployment Setup

### Step 1: Verify Required Secrets in GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Verify these secrets already exist (from MCP/backend deployments):

```yaml
# Server Access (from backend/MCP deployments)
PRODUCTION_HOST: your-server.com
PRODUCTION_USER: your-username  
PRODUCTION_SSH_KEY: (SSH private key)

# AI Configuration (from MCP deployment)
OPENAI_API_KEY: sk-proj-xxxxx       # Required
DEEPSEEK_API_KEY: sk-xxxxx         # Optional fallback
AI_PROVIDER: openai                 # Optional

# Integration Keys (from backend/MCP deployments)
WILDEDITOR_MCP_KEY: (MCP server key)
WILDEDITOR_API_KEY: (backend API key)
```

If any secrets are missing, refer to the MCP or backend deployment guides to set them up first.

### Step 2: Verify Docker Network on Server

SSH into your production server and verify the Docker network exists:

```bash
# SSH into server
ssh luminari@luminarimud.com

# Check if network exists
docker network ls | grep wildeditor-network

# If not exists, create it
docker network create wildeditor-network
```

### Step 3: Trigger Deployment

The Chat Agent will deploy automatically when you push changes to the `apps/agent/` directory:

```bash
# Make any change in apps/agent/
git add .
git commit -m "Deploy chat agent service"
git push origin main
```

Or manually trigger deployment:
1. Go to GitHub repository → **Actions** tab
2. Select **Deploy Chat Agent** workflow
3. Click **Run workflow** → **Run workflow**

### Step 4: Verify Deployment

After deployment completes, verify the service is running:

```bash
# SSH into server
ssh luminari@luminarimud.com

# Check container status
docker ps | grep wildeditor-chat-agent

# Check logs
docker logs wildeditor-chat-agent

# Test health endpoint
curl http://localhost:8002/health/

# Test from outside (if port is exposed)
curl https://luminarimud.com:8002/health/
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Container Won't Start
```bash
# Check logs
docker logs wildeditor-chat-agent

# Common issues:
# - Missing API key: Add OPENAI_API_KEY or ANTHROPIC_API_KEY
# - Wrong MODEL_PROVIDER: Must be "openai" or "anthropic"
# - Port conflict: Check nothing else is on port 8002
```

#### 2. Can't Connect to MCP/Backend
```bash
# Verify containers are on same network
docker network inspect wildeditor-network

# Should show all three containers:
# - wildeditor-backend
# - wildeditor-mcp  
# - wildeditor-chat-agent
```

#### 3. Authentication Failures
```bash
# Verify API keys match
docker exec wildeditor-chat-agent env | grep API_KEY
docker exec wildeditor-mcp env | grep API_KEY
```

#### 4. GitHub Actions Failing
- Check secret names are exactly as specified (case-sensitive)
- Verify SSH key has no extra spaces or newlines
- Ensure VPS_USER has docker permissions

## 📊 Monitoring

### View Logs
```bash
# Live logs
docker logs -f wildeditor-chat-agent

# Last 100 lines
docker logs --tail 100 wildeditor-chat-agent

# Logs since specific time
docker logs --since 1h wildeditor-chat-agent
```

### Check Resource Usage
```bash
# Container stats
docker stats wildeditor-chat-agent

# Detailed inspection
docker inspect wildeditor-chat-agent
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8002/health/

# Ready check (all components initialized)
curl http://localhost:8002/health/ready

# API documentation
curl http://localhost:8002/docs
```

## 🔄 Updating the Service

### Update Configuration
To update environment variables without redeploying code:

```bash
# SSH into server
ssh luminari@luminarimud.com

# Edit docker-compose file
cd /home/luminari/wildeditor/apps/agent
nano docker-compose.yml

# Restart with new config
docker-compose down
docker-compose up -d
```

### Update Code
Push changes to GitHub and the workflow will automatically:
1. Pull latest code
2. Rebuild container
3. Restart service with new code

## 🛡️ Security Best Practices

1. **Never commit API keys** to the repository
2. **Use GitHub Secrets** for all sensitive data
3. **Rotate API keys** periodically
4. **Limit SSH key permissions** to deployment only
5. **Monitor usage** of AI API keys for unexpected activity
6. **Use HTTPS** for production frontend URL

## 📝 Quick Reference

### Minimum Required Secrets Checklist
- [ ] `VPS_HOST` - Server hostname
- [ ] `VPS_USER` - SSH username  
- [ ] `VPS_SSH_KEY` - SSH private key
- [ ] `MODEL_PROVIDER` - Either "openai" or "anthropic"
- [ ] `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - AI service key
- [ ] `MODEL_NAME` - Specific model to use
- [ ] `MCP_API_KEY` - For MCP server integration
- [ ] `BACKEND_API_KEY` - For backend API integration

### Service URLs
- **Chat Agent**: `http://localhost:8002`
- **MCP Server**: `http://localhost:8001`  
- **Backend API**: `http://localhost:8000`
- **Frontend**: `https://wildedit.luminarimud.com`

### Docker Commands
```bash
# View status
docker ps | grep wildeditor

# Restart service
docker restart wildeditor-chat-agent

# Stop service
docker stop wildeditor-chat-agent

# Remove and recreate
docker rm -f wildeditor-chat-agent
cd /home/luminari/wildeditor/apps/agent
docker-compose up -d
```

## 🆘 Support

If you encounter issues not covered here:
1. Check the [Chat Agent README](CHAT_AGENT_README.md)
2. Review the [Implementation Guide](../docs/agent/IMPLEMENTATION_GUIDE.md)
3. Check container logs for specific error messages
4. Verify all secrets are correctly set in GitHub
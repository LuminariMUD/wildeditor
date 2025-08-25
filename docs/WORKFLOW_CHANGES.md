# GitHub Actions Workflow Changes for AI Support

## Overview

To enable AI provider support in the MCP deployment workflow, the following changes need to be applied to `.github/workflows/mcp-deploy.yml`.

**Note**: These changes require admin access or a user with the `workflow` scope to apply directly. If you don't have these permissions, create a pull request or ask an admin to apply these changes.

## Required Changes

### 1. Add AI Provider Environment Variables (Line ~217)

In the "Deploy MCP server to production" step, add the AI provider environment variables:

**Change from:**
```yaml
      - name: Deploy MCP server to production
        env:
          WILDEDITOR_MCP_KEY: ${{ secrets.WILDEDITOR_MCP_KEY }}
          WILDEDITOR_API_KEY: ${{ secrets.WILDEDITOR_API_KEY }}
        run: |
```

**Change to:**
```yaml
      - name: Deploy MCP server to production
        env:
          WILDEDITOR_MCP_KEY: ${{ secrets.WILDEDITOR_MCP_KEY }}
          WILDEDITOR_API_KEY: ${{ secrets.WILDEDITOR_API_KEY }}
          # AI Provider Keys
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          AI_PROVIDER: ${{ secrets.AI_PROVIDER }}
          OPENAI_MODEL: ${{ secrets.OPENAI_MODEL }}
          ANTHROPIC_MODEL: ${{ secrets.ANTHROPIC_MODEL }}
          OLLAMA_BASE_URL: ${{ secrets.OLLAMA_BASE_URL }}
          OLLAMA_MODEL: ${{ secrets.OLLAMA_MODEL }}
        run: |
```

### 2. Update Docker Container Environment Variables (Line ~313)

In the Docker run command within the deployment script, add the AI environment variables:

**Change from:**
```bash
          $DOCKER_CMD run -d \
            --name $CONTAINER_NAME \
            --restart unless-stopped \
            --network host \
            -e WILDEDITOR_MCP_KEY="$MCP_KEY" \
            -e WILDEDITOR_API_KEY="$MCP_BACKEND_KEY" \
            -e WILDEDITOR_BACKEND_URL="http://localhost:8000" \
            -e ENVIRONMENT="production" \
            -e DEBUG="false" \
            -e PORT="8001" \
            -e LOG_LEVEL="INFO" \
            -v $HOME/logs/wildeditor-mcp:/var/log/wildeditor-mcp \
            $DOCKER_IMAGE
```

**Change to:**
```bash
          $DOCKER_CMD run -d \
            --name $CONTAINER_NAME \
            --restart unless-stopped \
            --network host \
            -e WILDEDITOR_MCP_KEY="$MCP_KEY" \
            -e WILDEDITOR_API_KEY="$MCP_BACKEND_KEY" \
            -e WILDEDITOR_BACKEND_URL="http://localhost:8000" \
            -e ENVIRONMENT="production" \
            -e DEBUG="false" \
            -e PORT="8001" \
            -e LOG_LEVEL="INFO" \
            -e AI_PROVIDER="${AI_PROVIDER:-none}" \
            -e OPENAI_API_KEY="$OPENAI_API_KEY" \
            -e OPENAI_MODEL="${OPENAI_MODEL:-gpt-4-turbo-preview}" \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            -e ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-claude-3-opus-20240229}" \
            -e OLLAMA_BASE_URL="$OLLAMA_BASE_URL" \
            -e OLLAMA_MODEL="${OLLAMA_MODEL:-llama2}" \
            -v $HOME/logs/wildeditor-mcp:/var/log/wildeditor-mcp \
            $DOCKER_IMAGE
```

### 3. Pass Environment Variables Through SSH (Line ~398)

When executing the deployment script via SSH, pass the AI environment variables:

**Change from:**
```bash
          ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }} "
            chmod +x /tmp/deploy-mcp.sh
            export MCP_KEY='$WILDEDITOR_MCP_KEY'
            export MCP_BACKEND_KEY='$WILDEDITOR_API_KEY'
            /tmp/deploy-mcp.sh
          "
```

**Change to:**
```bash
          ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }} "
            chmod +x /tmp/deploy-mcp.sh
            export MCP_KEY='$WILDEDITOR_MCP_KEY'
            export MCP_BACKEND_KEY='$WILDEDITOR_API_KEY'
            export AI_PROVIDER='${AI_PROVIDER:-none}'
            export OPENAI_API_KEY='$OPENAI_API_KEY'
            export OPENAI_MODEL='${OPENAI_MODEL:-gpt-4-turbo-preview}'
            export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'
            export ANTHROPIC_MODEL='${ANTHROPIC_MODEL:-claude-3-opus-20240229}'
            export OLLAMA_BASE_URL='$OLLAMA_BASE_URL'
            export OLLAMA_MODEL='${OLLAMA_MODEL:-llama2}'
            /tmp/deploy-mcp.sh
          "
```

### 4. Update Deployment Notification (Line ~460)

Update the deployment notification to show AI provider status:

**Change from:**
```javascript
            const output = `#### 🤖 MCP Server Deployment Successful!\n
            - **Environment**: Production
            - **Version**: \`${{ github.sha }}\`
            - **MCP API URL**: http://${{ secrets.PRODUCTION_HOST }}:8001
            - **Health Check**: ✅ Passing
            - **Authentication**: 🔐 MCP Key Required
            - **Tools**: 5 Wilderness Management Tools
            - **Resources**: 7 Knowledge Resources  
            - **Prompts**: 5 AI Content Generation Templates
            - **Deployed by**: @${{ github.actor }}
            
            The MCP server is now live and ready for AI agent integration!
```

**Change to:**
```javascript
            const output = `#### 🤖 MCP Server Deployment Successful!\n
            - **Environment**: Production
            - **Version**: \`${{ github.sha }}\`
            - **MCP API URL**: http://${{ secrets.PRODUCTION_HOST }}:8001
            - **Health Check**: ✅ Passing
            - **Authentication**: 🔐 MCP Key Required
            - **AI Provider**: ${process.env.AI_PROVIDER || 'Template Fallback'}
            - **Tools**: 14 Wilderness Management Tools (5 with AI)
            - **Resources**: 7 Knowledge Resources  
            - **Prompts**: 5 AI Content Generation Templates
            - **Deployed by**: @${{ github.actor }}
            
            The MCP server is now live with AI-powered description generation!
```

## How to Apply These Changes

### Option 1: Direct Edit (Requires Admin Access)
1. Navigate to `.github/workflows/mcp-deploy.yml` in the GitHub web interface
2. Click the edit button (pencil icon)
3. Apply the changes above
4. Commit directly to main branch

### Option 2: Pull Request (Recommended)
1. Create a new branch
2. Apply the changes to `.github/workflows/mcp-deploy.yml`
3. Create a pull request
4. Have an admin with workflow permissions merge it

### Option 3: Local Application (For Admins)
```bash
# Clone the repository
git clone https://github.com/LuminariMUD/wildeditor.git
cd wildeditor

# Create a new branch
git checkout -b feat/ai-provider-workflow

# Edit the workflow file
nano .github/workflows/mcp-deploy.yml

# Apply the changes described above

# Commit and push
git add .github/workflows/mcp-deploy.yml
git commit -m "feat: Add AI provider support to MCP deployment workflow"
git push origin feat/ai-provider-workflow

# Create pull request via GitHub UI
```

## Verification

After applying these changes:

1. Add the required secrets as documented in [GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md)
2. Push to main branch to trigger deployment
3. Check the deployment logs in GitHub Actions
4. Verify AI provider is active:
   ```bash
   curl -H "X-API-Key: YOUR_MCP_KEY" \
     http://your-server:8001/mcp/status
   ```

## Support

If you encounter issues applying these changes:
- Ensure you have the necessary permissions
- Contact a repository admin
- Open an issue describing the problem
# MCP Server Deployment Setup Guide

## 🔑 **GitHub Secrets Configuration**

Add these new secrets to your GitHub repository (Settings → Secrets and variables → Actions):

### **MCP Server Authentication Keys**

1. **WILDEDITOR_MCP_KEY**
   - **Purpose**: Authentication for AI agents to access MCP server
   - **Generate with PowerShell**:
   ```powershell
   $bytes = New-Object byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); [Convert]::ToBase64String($bytes)
   ```
   - **Example**: `J8K9L0MnOpQrStUvWxYz1234567890ABCDefGhIjKlMnOpQr=`

**Note**: The MCP server will use your existing `WILDEDITOR_API_KEY` for backend communication, so no additional backend key is needed.

## 🖥️ **Server Setup Requirements**

Your server needs these additional configurations:

### **1. Install MCP Server Dependencies**
```bash
# SSH into your server
ssh your-user@your-server

# Navigate to deployment directory
cd /opt/wildeditor-backend

# Install Python MCP server dependencies
sudo apt-get update
sudo apt-get install python3.11-venv

# Create MCP virtual environment
python3.11 -m venv /opt/wildeditor-mcp-venv
source /opt/wildeditor-mcp-venv/bin/activate
pip install fastapi uvicorn httpx python-dotenv pydantic
```

### **2. Create MCP Application Directory**
```bash
# Create MCP server directory
sudo mkdir -p /opt/wildeditor-mcp
sudo chown $USER:$USER /opt/wildeditor-mcp
sudo mkdir -p /var/log/wildeditor-mcp
sudo chown $USER:$USER /var/log/wildeditor-mcp
```

### **3. Configure Firewall (if needed)**
```bash
# Allow MCP server port
sudo ufw allow 8001/tcp
sudo ufw reload

# Verify ports
sudo ufw status
```

## 🐳 **Docker Deployment Configuration**

### **Option 1: Same-Server Docker Compose (Recommended)**

Create `/opt/wildeditor/docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    image: ghcr.io/luminarimud/wildeditor-backend:latest
    container_name: wildeditor-backend
    ports:
      - "8000:8000"
    environment:
      - MYSQL_DATABASE_URL=${MYSQL_DATABASE_URL}
      - WILDEDITOR_API_KEY=${WILDEDITOR_API_KEY}
      - WILDEDITOR_MCP_BACKEND_KEY=${WILDEDITOR_MCP_BACKEND_KEY}
      - ENVIRONMENT=production
      - DEBUG=false
    restart: unless-stopped
    volumes:
      - /var/log/wildeditor:/var/log/wildeditor

  mcp-server:
    image: ghcr.io/luminarimud/wildeditor-mcp:latest
    container_name: wildeditor-mcp
    ports:
      - "8001:8001"
    environment:
      - WILDEDITOR_MCP_KEY=${WILDEDITOR_MCP_KEY}
      - WILDEDITOR_MCP_BACKEND_KEY=${WILDEDITOR_MCP_BACKEND_KEY}
      - WILDEDITOR_BACKEND_URL=http://backend:8000
      - ENVIRONMENT=production
      - DEBUG=false
    restart: unless-stopped
    volumes:
      - /var/log/wildeditor-mcp:/var/log/wildeditor-mcp
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    container_name: wildeditor-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    restart: unless-stopped
    depends_on:
      - backend
      - mcp-server
```

### **Option 2: Separate Container Deployment**

If using existing GitHub Actions, extend your deployment script:
```bash
# Add to your existing deployment script
DOCKER_MCP_IMAGE="${{ env.REGISTRY }}/luminarimud/wildeditor-mcp:latest"
MCP_CONTAINER_NAME="wildeditor-mcp"

# Pull MCP image
docker pull $DOCKER_MCP_IMAGE

# Stop existing MCP container
docker stop $MCP_CONTAINER_NAME || true
docker rm $MCP_CONTAINER_NAME || true

# Start MCP container
docker run -d \
  --name $MCP_CONTAINER_NAME \
  --restart unless-stopped \
  -p 8001:8001 \
  -e WILDEDITOR_MCP_KEY="$WILDEDITOR_MCP_KEY" \
  -e WILDEDITOR_MCP_BACKEND_KEY="$WILDEDITOR_MCP_BACKEND_KEY" \
  -e WILDEDITOR_BACKEND_URL="http://localhost:8000" \
  -e ENVIRONMENT="production" \
  -e DEBUG="false" \
  -v /var/log/wildeditor-mcp:/var/log/wildeditor-mcp \
  $DOCKER_MCP_IMAGE
```

## 🔄 **GitHub Actions Workflow Extension**

### **Create New MCP Deployment Workflow**

Create `.github/workflows/mcp-deploy.yml`:
```yaml
name: MCP Server CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'apps/mcp/**'
      - 'packages/auth/**'
      - '.github/workflows/mcp-deploy.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'apps/mcp/**'

env:
  PYTHON_VERSION: '3.11'
  DOCKER_IMAGE: 'wildeditor-mcp'
  REGISTRY: 'ghcr.io'

jobs:
  test-mcp:
    name: Test MCP Server
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install dependencies
        run: |
          cd apps/mcp
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -e ../../packages/auth
          
      - name: Run tests
        run: |
          cd apps/mcp
          pytest tests/ -v
          
      - name: Test server startup
        run: |
          cd apps/mcp
          export WILDEDITOR_MCP_KEY="test-key"
          export WILDEDITOR_MCP_BACKEND_KEY="test-backend-key"
          export WILDEDITOR_BACKEND_URL="http://localhost:8000"
          python -c "
          from src.main import app
          from fastapi.testclient import TestClient
          client = TestClient(app)
          response = client.get('/health')
          assert response.status_code == 200
          print('✅ MCP server startup test passed')
          "

  build-mcp-image:
    name: Build MCP Docker Image
    runs-on: ubuntu-latest
    needs: test-mcp
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/luminarimud/wildeditor-mcp
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
            
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: apps/mcp/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-mcp:
    name: Deploy MCP Server
    runs-on: ubuntu-latest
    needs: [test-mcp, build-mcp-image]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    environment:
      name: production
      
    steps:
      - name: Deploy to production server
        env:
          WILDEDITOR_MCP_KEY: ${{ secrets.WILDEDITOR_MCP_KEY }}
          WILDEDITOR_MCP_BACKEND_KEY: ${{ secrets.WILDEDITOR_MCP_BACKEND_KEY }}
        run: |
          ssh -o StrictHostKeyChecking=no ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }} "
            # Pull latest MCP image
            docker pull ghcr.io/luminarimud/wildeditor-mcp:latest
            
            # Stop existing MCP container
            docker stop wildeditor-mcp || true
            docker rm wildeditor-mcp || true
            
            # Start new MCP container
            docker run -d \
              --name wildeditor-mcp \
              --restart unless-stopped \
              -p 8001:8001 \
              -e WILDEDITOR_MCP_KEY='$WILDEDITOR_MCP_KEY' \
              -e WILDEDITOR_MCP_BACKEND_KEY='$WILDEDITOR_MCP_BACKEND_KEY' \
              -e WILDEDITOR_BACKEND_URL='http://localhost:8000' \
              -e ENVIRONMENT='production' \
              -e DEBUG='false' \
              -v /var/log/wildeditor-mcp:/var/log/wildeditor-mcp \
              ghcr.io/luminarimud/wildeditor-mcp:latest
              
            # Wait for health check
            sleep 10
            curl -f http://localhost:8001/health || exit 1
            echo '✅ MCP server deployed successfully!'
          "
```

### **Or Extend Existing Backend Workflow**

Add MCP deployment to your existing `backend-deploy.yml`:

```yaml
# Add after backend deployment steps
- name: Deploy MCP Server
  env:
    WILDEDITOR_MCP_KEY: ${{ secrets.WILDEDITOR_MCP_KEY }}
    WILDEDITOR_MCP_BACKEND_KEY: ${{ secrets.WILDEDITOR_MCP_BACKEND_KEY }}
  run: |
    # Add MCP deployment script here
```

## ✅ **Quick Setup Checklist**

1. **✅ Generate and add GitHub secrets**:
   - `WILDEDITOR_MCP_KEY`
   - `WILDEDITOR_MCP_BACKEND_KEY`

2. **✅ Prepare server**:
   - Create MCP directories
   - Configure firewall for port 8001
   - Test Docker access

3. **✅ Create MCP Dockerfile**:
   ```dockerfile
   # apps/mcp/Dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY packages/auth packages/auth
   RUN pip install -e packages/auth
   
   COPY apps/mcp/src .
   
   EXPOSE 8001
   
   CMD ["python", "run_dev.py"]
   ```

4. **✅ Update nginx configuration** (if using reverse proxy):
   ```nginx
   # Add to nginx.conf
   location /mcp/ {
       proxy_pass http://localhost:8001/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

5. **✅ Test deployment**:
   ```bash
   # After deployment
   curl http://your-server:8001/health
   curl -H "X-API-Key: your-mcp-key" http://your-server:8001/mcp/status
   ```

## 🚀 **Ready for Production!**

Once you've completed these steps:
1. Push changes to trigger GitHub Actions
2. MCP server will deploy alongside your backend
3. AI agents can connect to `http://your-server:8001`
4. Use the MCP key for authentication

The MCP server will be fully integrated with your existing infrastructure! 🎉

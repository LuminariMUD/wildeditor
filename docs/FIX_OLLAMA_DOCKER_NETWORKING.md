# Fix Ollama Docker Networking Issue

## Problem
The MCP Docker container cannot reach Ollama at `localhost:11434` because Docker containers have network isolation. Even with `--network host`, the container might not properly resolve localhost to the host machine.

## Solution Options

### Option 1: Use Host IP Instead of Localhost (Recommended)

Update the GitHub Secret:
- Go to: https://github.com/LuminariMUD/wildeditor/settings/secrets/actions
- Change `OLLAMA_BASE_URL` from `http://localhost:11434` to one of:
  - `http://host.docker.internal:11434` (if Docker supports it)
  - `http://172.17.0.1:11434` (Docker bridge gateway)
  - `http://74.208.126.44:11434` (server's public IP - least secure)

### Option 2: Configure Ollama to Listen on All Interfaces

1. Edit Ollama service configuration:
```bash
# Create override for Ollama service
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo cat > /etc/systemd/system/ollama.service.d/override.conf << EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

2. Then update GitHub Secret:
- `OLLAMA_BASE_URL` = `http://172.17.0.1:11434`

### Option 3: Run MCP Without Docker (Direct Python)

Since you're on the production server, you could run MCP directly:

```bash
# Stop Docker container
sudo docker stop wildeditor-mcp

# Run directly with Python
cd /home/luminari/wildeditor/apps/mcp
source venv/bin/activate

# Set environment variables
export WILDEDITOR_MCP_KEY="xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="
export WILDEDITOR_API_KEY="0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"
export WILDEDITOR_BACKEND_URL="http://localhost:8000"
export AI_PROVIDER="openai"
export OPENAI_API_KEY="<your-key>"
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2:1b"

# Run the server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Quick Test

Test which URLs work from the Docker container:

```bash
# Test different URLs
for url in "http://localhost:11434" "http://172.17.0.1:11434" "http://host.docker.internal:11434"; do
  echo "Testing $url..."
  sudo docker run --rm --network host curlimages/curl:latest \
    curl -s $url/api/tags > /dev/null 2>&1 && echo "✅ $url works" || echo "❌ $url fails"
done
```

## Recommended Fix

1. **Update GitHub Secret**:
   - `OLLAMA_BASE_URL` = `http://172.17.0.1:11434`

2. **Ensure Ollama listens on Docker bridge**:
```bash
# Check if Ollama is accessible from Docker bridge
curl http://172.17.0.1:11434/api/tags
```

3. **Redeploy MCP** after updating the secret

This should allow the MCP Docker container to reach Ollama through the Docker bridge network.
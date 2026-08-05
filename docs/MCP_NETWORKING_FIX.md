# MCP Docker Networking Fix

## 🔍 **Problem Identified**

The MCP server was unable to connect to the backend API because of a **docker networking mismatch**:

- **Backend**: Deployed with `--network host` (shares host network)
- **MCP Server**: Deployed with default bridge networking + port mapping `-p 8001:8001`

When MCP server tried to connect to `http://localhost:8000`, it was looking inside its own container, not the host machine where the backend runs.

## ✅ **Solution Applied**

Updated `.github/workflows/mcp-deploy.yml` to use **host networking** for the MCP container, matching the backend deployment:

```bash
# Before (broken)
docker run -d \
  --name wildeditor-mcp \
  --restart unless-stopped \
  -p 8001:8001 \
  # ... other args

# After (fixed)
docker run -d \
  --name wildeditor-mcp \
  --restart unless-stopped \
  --network host \
  # ... other args (no port mapping needed with host networking)
```

## 🔧 **How Host Networking Works**

With `--network host`:
- Both containers share the host machine's network stack
- Backend binds to `host:8000` 
- MCP server binds to `host:8001`
- MCP can reach backend via `http://localhost:8000` ✅

## 🧪 **Testing the Fix**

After redeployment, test MCP → Backend connectivity:

```bash
# 1. Test backend health (should work)
curl http://luminarimud.com:8000/api/health

# 2. Test MCP health (should work)  
curl http://luminarimud.com:8001/health

# 3. Test MCP can reach backend (the critical test)
curl -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" \
     "http://luminarimud.com:8001/mcp/tools/analyze_terrain_at_coordinates" \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"x": 0, "y": 0}'
```

## 🔄 **Alternative Solutions Considered**

1. **Docker Compose Network** (better long-term)
   - Create shared network: `wildeditor`
   - MCP connects to: `http://wildeditor-backend:8000`
   - Requires deployment refactoring

2. **Bridge Networking with Host IP**
   - Auto-detect host IP in container
   - MCP connects to: `http://{host_ip}:8000`
   - More complex, host networking is simpler

3. **Container Linking** (deprecated)
   - Not recommended for modern deployments

## 📝 **Verification Steps**

1. Redeploy MCP container with new workflow
2. Check container networking: `docker inspect wildeditor-mcp`
3. Test internal connectivity from MCP container
4. Verify PowerShell test script works end-to-end

The fix should resolve the "connection refused" errors when MCP tries to call backend APIs.

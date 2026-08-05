# 🚀 MCP Networking Fix - Deployment Checklist

## ✅ **Pre-Deployment Verification**

1. **Confirm Current Issue**
   ```bash
   # This should fail before the fix
   curl -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{"x": 0, "y": 0}' \
        "http://luminarimud.com:8001/mcp/tools/analyze_terrain_at_coordinates"
   ```

2. **Check Current Container Networking**
   ```bash
   # Should show different network modes
   docker inspect wildeditor-backend --format '{{.HostConfig.NetworkMode}}'  # Should be "host"
   docker inspect wildeditor-mcp --format '{{.HostConfig.NetworkMode}}'      # Should be "default"
   ```

## 🔧 **Deployment Steps**

1. **Deploy Updated MCP Container**
   ```bash
   # Trigger GitHub Actions deployment or run manually:
   # The updated .github/workflows/mcp-deploy.yml will use --network host
   ```

2. **Verify New Container Settings**
   ```bash
   # Both should now show "host" networking
   docker inspect wildeditor-backend --format '{{.HostConfig.NetworkMode}}'
   docker inspect wildeditor-mcp --format '{{.HostConfig.NetworkMode}}'
   ```

## ✅ **Post-Deployment Testing**

### **Quick Tests**
```bash
# 1. Backend health
curl http://luminarimud.com:8000/api/health

# 2. MCP health  
curl http://luminarimud.com:8001/health

# 3. MCP → Backend connectivity
curl -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"x": 0, "y": 0}' \
     "http://luminarimud.com:8001/mcp/tools/analyze_terrain_at_coordinates"
```

### **Comprehensive Tests**
```bash
# Run the full test suite
./tests/test-mcp-networking-fix.sh

# Or on Windows
.\tests\test-mcp-networking-fix.ps1
```

### **Original PowerShell Tests**
```powershell
# Should now work end-to-end
.\tests\test-terrain-bridge-api.ps1
```

## 🔍 **Expected Results**

### **Before Fix (Broken)**
```json
{
  "error": "Failed to analyze region: Connection refused",
  "details": "Cannot connect to http://localhost:8000"
}
```

### **After Fix (Working)**
```json
{
  "result": {
    "terrain": {
      "x": 0,
      "y": 0,
      "elevation": 123,
      "sector_name": "plains"
    },
    "analysis": "Terrain analysis complete"
  }
}
```

## 🚨 **Troubleshooting**

### **If Tests Still Fail**

1. **Check Container Logs**
   ```bash
   docker logs wildeditor-mcp --tail 50
   docker logs wildeditor-backend --tail 50
   ```

2. **Verify Environment Variables**
   ```bash
   docker inspect wildeditor-mcp | grep -A 10 "Env"
   ```

3. **Test Internal Connectivity**
   ```bash
   # From within MCP container
   docker exec wildeditor-mcp curl http://localhost:8000/api/health
   ```

4. **Check Port Bindings**
   ```bash
   netstat -tlnp | grep -E ':(8000|8001)'
   # Both should show 0.0.0.0:port with host networking
   ```

### **Rollback Plan**
If the fix causes issues:
```bash
# Revert to bridge networking
docker stop wildeditor-mcp
docker rm wildeditor-mcp
docker run -d \
  --name wildeditor-mcp \
  --restart unless-stopped \
  -p 8001:8001 \
  # ... other original parameters
```

## 📝 **Success Criteria**

- ✅ MCP container uses host networking
- ✅ MCP health endpoint responds
- ✅ Backend health endpoint responds  
- ✅ MCP tools can call backend APIs
- ✅ PowerShell test script passes all tests
- ✅ No connection refused errors in MCP logs

## 🔄 **Next Steps After Fix**

1. Monitor for any performance impact
2. Consider migrating to docker-compose networking for better isolation
3. Update documentation with networking requirements
4. Add monitoring alerts for connectivity issues

#!/bin/bash
# SSH into your server and run these commands to test the MCP server locally

echo "🔍 Testing MCP Server on localhost (inside server)"

# 1. Check if container is running
echo "1. Container Status:"
docker ps | grep wildeditor-mcp

# 2. Check if port is listening locally  
echo -e "\n2. Port Status:"
ss -tlnp | grep :8001

# 3. Test health endpoint locally
echo -e "\n3. Health Check:"
curl -s http://localhost:8001/health | jq . || curl -s http://localhost:8001/health

# 4. Test MCP status with authentication
echo -e "\n4. MCP Status (with auth):"
curl -s -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" http://localhost:8001/mcp/status | jq . || curl -s -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" http://localhost:8001/mcp/status

# 5. Test MCP tools
echo -e "\n5. MCP Tools:"
curl -s -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" http://localhost:8001/mcp/tools | jq . || curl -s -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" http://localhost:8001/mcp/tools

# 6. Test MCP resources
echo -e "\n6. MCP Resources:"
curl -s -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" http://localhost:8001/mcp/resources | jq . || curl -s -H "X-API-Key: xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=" http://localhost:8001/mcp/resources

echo -e "\n✅ Local testing complete!"

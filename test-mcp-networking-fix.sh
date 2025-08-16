#!/bin/bash
# Test script to verify MCP → Backend connectivity after networking fix

echo "🔍 Testing MCP Docker Networking Fix"
echo "======================================"

# Configuration
MCP_URL="http://luminarimud.com:8001"
BACKEND_URL="http://luminarimud.com:8000"
MCP_API_KEY="xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="
BACKEND_API_KEY=""

echo ""
echo "1. 🏥 Testing Backend Health..."
if curl -s -f "$BACKEND_URL/api/health" >/dev/null; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend health check failed"
    exit 1
fi

echo ""
echo "2. 🏥 Testing MCP Health..."
if curl -s -f "$MCP_URL/health" >/dev/null; then
    echo "   ✅ MCP server is healthy"
else
    echo "   ❌ MCP health check failed"
    exit 1
fi

echo ""
echo "3. 🔗 Testing MCP → Backend Connectivity..."
echo "   Calling MCP tool that requires backend access..."

response=$(curl -s -w "%{http_code}" \
  -H "X-API-Key: $MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"x": 0, "y": 0}' \
  "$MCP_URL/mcp/tools/analyze_terrain_at_coordinates" \
  -o /tmp/mcp_response.json)

http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "   ✅ MCP successfully connected to backend!"
    echo "   📄 Response preview:"
    head -n 3 /tmp/mcp_response.json | sed 's/^/      /'
elif [ "$http_code" = "500" ]; then
    echo "   ⚠️  MCP received request but may have backend connection issues"
    echo "   📄 Error details:"
    cat /tmp/mcp_response.json | sed 's/^/      /'
else
    echo "   ❌ MCP tool call failed (HTTP $http_code)"
    echo "   📄 Response:"
    cat /tmp/mcp_response.json | sed 's/^/      /'
fi

echo ""
echo "4. 🔍 Checking Container Networking..."
if command -v docker >/dev/null 2>&1; then
    echo "   🐳 MCP Container Network Mode:"
    docker inspect wildeditor-mcp --format '{{.HostConfig.NetworkMode}}' | sed 's/^/      /'
    
    echo "   🐳 Backend Container Network Mode:"
    docker inspect wildeditor-backend --format '{{.HostConfig.NetworkMode}}' | sed 's/^/      /'
else
    echo "   ⚠️  Docker not available in this environment"
fi

echo ""
echo "5. 📊 Summary"
echo "   - Backend: $BACKEND_URL"
echo "   - MCP: $MCP_URL"
echo "   - Test completed at: $(date)"

# Cleanup
rm -f /tmp/mcp_response.json

echo ""
echo "✅ Networking verification complete!"

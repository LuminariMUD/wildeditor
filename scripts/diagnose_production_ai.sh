#!/bin/bash
# Diagnostic script for production AI integration
# Run this on the production server

echo "🔍 Production AI Integration Diagnostic"
echo "========================================"

echo ""
echo "1️⃣ Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    ollama version
else
    echo "❌ Ollama is NOT installed"
    echo "   Install with: curl -fsSL https://ollama.ai/install.sh | sh"
fi

echo ""
echo "2️⃣ Checking Ollama service..."
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama service is running"
else
    echo "❌ Ollama service is NOT running"
    echo "   Start with: sudo systemctl start ollama"
fi

echo ""
echo "3️⃣ Checking Ollama API..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama API is responsive"
    echo "   Models available:"
    curl -s http://localhost:11434/api/tags | jq -r '.models[].name' | sed 's/^/   - /'
else
    echo "❌ Ollama API is NOT responsive"
fi

echo ""
echo "4️⃣ Checking llama3.2:1b model..."
if curl -s http://localhost:11434/api/tags | grep -q "llama3.2:1b"; then
    echo "✅ llama3.2:1b model is installed"
else
    echo "❌ llama3.2:1b model is NOT installed"
    echo "   Install with: ollama pull llama3.2:1b"
fi

echo ""
echo "5️⃣ Checking MCP container environment..."
if docker ps | grep -q wildeditor-mcp; then
    echo "✅ MCP container is running"
    echo "   Environment variables:"
    docker exec wildeditor-mcp env | grep -E "AI_PROVIDER|OPENAI|OLLAMA" | sed 's/^/   /'
else
    echo "❌ MCP container is NOT running"
fi

echo ""
echo "6️⃣ Testing Ollama from MCP container..."
if docker ps | grep -q wildeditor-mcp; then
    if docker exec wildeditor-mcp curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ MCP container CAN reach Ollama"
    else
        echo "❌ MCP container CANNOT reach Ollama"
        echo "   This is the likely issue!"
    fi
else
    echo "⚠️ Cannot test - MCP container not running"
fi

echo ""
echo "7️⃣ Checking MCP logs for AI errors..."
if docker ps | grep -q wildeditor-mcp; then
    echo "Recent AI-related logs:"
    docker logs wildeditor-mcp 2>&1 | grep -i "ai\|ollama\|openai" | tail -5 | sed 's/^/   /'
else
    echo "⚠️ Cannot check logs - MCP container not running"
fi

echo ""
echo "========================================"
echo "📊 SUMMARY"
echo "========================================"
echo ""
echo "For AI fallback to work, ALL of these must be true:"
echo "1. Ollama must be installed ✓"
echo "2. Ollama service must be running ✓"
echo "3. llama3.2:1b model must be installed ✓"
echo "4. MCP container must be able to reach localhost:11434 ✓"
echo "5. Environment variables must be set correctly ✓"
echo ""
echo "Run this script on the production server to diagnose issues."
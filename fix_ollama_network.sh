#!/bin/bash
# Fix Ollama networking for Docker access

echo "🔧 Fixing Ollama Network Configuration"
echo "======================================"

# Check current Ollama binding
echo "Current Ollama binding:"
ss -tlnp 2>/dev/null | grep 11434 || netstat -tlnp 2>/dev/null | grep 11434

echo ""
echo "📝 Creating Ollama configuration to listen on all interfaces..."

# Create Ollama service override
cat > /tmp/ollama-override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

echo ""
echo "The following commands need to be run with sudo:"
echo ""
echo "sudo mkdir -p /etc/systemd/system/ollama.service.d/"
echo "sudo cp /tmp/ollama-override.conf /etc/systemd/system/ollama.service.d/override.conf"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl restart ollama"
echo ""
echo "After running these commands, Ollama will be accessible from Docker containers."
echo ""
echo "Then update the GitHub Secret:"
echo "  OLLAMA_BASE_URL = http://172.17.0.1:11434"
echo ""
echo "Or if Ollama is running as a regular process (not systemd), restart it with:"
echo "  OLLAMA_HOST=0.0.0.0:11434 ollama serve"
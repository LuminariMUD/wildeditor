#!/bin/bash

# Script to set up OpenAI configuration from Luminari-Source
# This script should NOT be committed to git

echo "=================================="
echo "OpenAI Setup from Luminari-Source"
echo "=================================="
echo ""

# Check if Luminari-Source .env exists
LUMINARI_ENV="/home/luminari/Luminari-Source/lib/.env"

if [ ! -f "$LUMINARI_ENV" ]; then
    echo "❌ Error: Luminari-Source .env not found at $LUMINARI_ENV"
    exit 1
fi

# Extract OpenAI key from Luminari-Source
OPENAI_KEY=$(grep "^OPENAI_API_KEY=" "$LUMINARI_ENV" | cut -d'=' -f2)

if [ -z "$OPENAI_KEY" ]; then
    echo "❌ Error: OpenAI API key not found in Luminari-Source .env"
    exit 1
fi

echo "✅ Found OpenAI API key in Luminari-Source"
echo ""

# Update MCP .env file
MCP_ENV="/home/luminari/wildeditor/apps/mcp/.env"

if [ -f "$MCP_ENV" ]; then
    # Backup existing .env
    cp "$MCP_ENV" "$MCP_ENV.backup"
    
    # Update the OpenAI key
    sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_KEY|" "$MCP_ENV"
    
    echo "✅ Updated MCP .env with OpenAI key"
else
    echo "❌ Error: MCP .env not found at $MCP_ENV"
    exit 1
fi

# Export for current session
export OPENAI_API_KEY="$OPENAI_KEY"

echo ""
echo "Configuration complete!"
echo "- OpenAI API key configured for MCP server"
echo "- Model: gpt-4o-mini (cost-effective)"
echo ""
echo "To test the configuration:"
echo "  export OPENAI_API_KEY='$OPENAI_KEY'"
echo "  source apps/mcp/venv/bin/activate"
echo "  python3 test_openai_simple.py"
echo ""
echo "⚠️  IMPORTANT: Do not commit the .env file with the actual API key!"
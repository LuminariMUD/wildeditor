#!/bin/bash

# GitHub Secrets Setup Script for Wildeditor MCP Server
# This script helps you configure the required GitHub Actions secrets

echo "=================================="
echo "GitHub Secrets Setup for Wildeditor"
echo "=================================="
echo ""
echo "This script will generate the necessary values for GitHub Actions secrets."
echo "You'll need to manually add these to your repository settings."
echo ""

# Function to generate random key
generate_key() {
    openssl rand -base64 32
}

# Generate authentication keys
echo "1. Generating Authentication Keys..."
MCP_KEY=$(generate_key)
API_KEY=$(generate_key)

echo "✅ Keys generated successfully"
echo ""

# Get OpenAI configuration from environment or use placeholder
# IMPORTANT: Replace with your actual OpenAI API key!
OPENAI_KEY="${OPENAI_API_KEY:-your-openai-api-key-here}"
OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}"

# Production server details (update these as needed)
PRODUCTION_HOST="luminarimud.com"
PRODUCTION_USER="root"

echo "=================================="
echo "GITHUB SECRETS TO ADD"
echo "=================================="
echo ""
echo "Go to: https://github.com/LuminariMUD/wildeditor/settings/secrets/actions"
echo "Click 'New repository secret' for each of the following:"
echo ""
echo "### Required Secrets ###"
echo ""
echo "WILDEDITOR_MCP_KEY:"
echo "$MCP_KEY"
echo ""
echo "WILDEDITOR_API_KEY:"
echo "$API_KEY"
echo ""
echo "PRODUCTION_HOST:"
echo "$PRODUCTION_HOST"
echo ""
echo "PRODUCTION_USER:"
echo "$PRODUCTION_USER"
echo ""
echo "PRODUCTION_SSH_KEY:"
echo "(Use your existing SSH private key for the server)"
echo ""
echo "### AI Provider Secrets ###"
echo ""
echo "AI_PROVIDER:"
echo "openai"
echo ""
echo "OPENAI_API_KEY:"
echo "$OPENAI_KEY"
echo ""
echo "OPENAI_MODEL:"
echo "$OPENAI_MODEL"
echo ""
echo "=================================="
echo "SUMMARY"
echo "=================================="
echo ""
echo "Total secrets to add: 8"
echo "- 5 Required (authentication & deployment)"
echo "- 3 AI Provider (OpenAI configuration)"
echo ""
echo "After adding these secrets:"
echo "1. Push any change to main branch to trigger deployment"
echo "2. Check GitHub Actions for deployment status"
echo "3. Test the MCP server at http://$PRODUCTION_HOST:8001/health"
echo ""
echo "AI Features enabled:"
echo "- Model: GPT-4o-mini (cost-effective)"
echo "- Max tokens: 500"
echo "- Temperature: 0.7"
echo "- Rate limits: 60/min, 1000/hour"
echo ""

# Save configuration to file for reference
cat > github_secrets_values.txt << EOF
# GitHub Secrets Configuration
# Generated: $(date)
# IMPORTANT: Keep this file secure and delete after use!

WILDEDITOR_MCP_KEY=$MCP_KEY
WILDEDITOR_API_KEY=$API_KEY
PRODUCTION_HOST=$PRODUCTION_HOST
PRODUCTION_USER=$PRODUCTION_USER
PRODUCTION_SSH_KEY=(Add your SSH private key)
AI_PROVIDER=openai
OPENAI_API_KEY=$OPENAI_KEY
OPENAI_MODEL=$OPENAI_MODEL
EOF

echo "✅ Configuration saved to: github_secrets_values.txt"
echo "   (Delete this file after adding secrets to GitHub)"
echo ""
echo "📚 Documentation:"
echo "   - Setup Guide: docs/GITHUB_SECRETS_SETUP.md"
echo "   - Quick Start: docs/GITHUB_SECRETS_QUICKSTART.md"
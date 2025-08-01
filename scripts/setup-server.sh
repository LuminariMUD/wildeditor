#!/bin/bash

# Server Setup Script for Wildeditor Backend Deployment
# This script prepares a Ubuntu/Debian server for Docker deployment

set -e

echo "🔧 Wildeditor Backend Server Setup"
echo "=================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Run as a regular user with sudo access."
    exit 1
fi

# Check if user has sudo access
echo "🔐 Checking sudo access..."
if ! sudo -n true 2>/dev/null; then
    echo "⚠️  This script requires sudo access. You may be prompted for your password."
    echo "Testing sudo access..."
    if ! sudo true; then
        echo "❌ Unable to obtain sudo access. Please ensure you have sudo privileges."
        exit 1
    fi
    echo "✅ Sudo access confirmed"
else
    echo "✅ Passwordless sudo access detected"
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    
    # Install dependencies
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up the stable repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker is already installed"
fi

# Add current user to docker group
if ! groups | grep -q docker; then
    echo "👤 Adding user to docker group..."
    sudo usermod -aG docker $USER
    echo "✅ User added to docker group"
    echo "⚠️  You need to log out and back in for group changes to take effect"
    NEED_RELOGIN=true
else
    echo "✅ User is already in docker group"
fi

# Start and enable Docker service
echo "🚀 Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/wildeditor-backend
sudo chown $USER:$USER /opt/wildeditor-backend

# Create log directory
echo "📝 Creating log directory..."
sudo mkdir -p /var/log/wildeditor
sudo chown $USER:$USER /var/log/wildeditor

# Install useful tools
echo "🛠️  Installing useful tools..."
sudo apt-get install -y curl wget htop

# Test Docker installation
echo "🧪 Testing Docker installation..."
if [ "${NEED_RELOGIN:-false}" = "true" ]; then
    echo "⚠️  Cannot test Docker without relogin. Please log out and back in, then run:"
    echo "   docker run hello-world"
else
    if docker run hello-world > /dev/null 2>&1; then
        echo "✅ Docker test successful"
    else
        echo "❌ Docker test failed. You may need to log out and back in."
    fi
fi

# Setup firewall (if ufw is available)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring firewall..."
    sudo ufw allow ssh
    sudo ufw allow 8000/tcp
    echo "✅ Firewall configured (SSH and port 8000 allowed)"
fi

echo ""
echo "🎉 Server setup completed!"
echo ""
echo "📋 Summary:"
echo "  - Docker installed and configured"
echo "  - User added to docker group"
echo "  - Application directory: /opt/wildeditor-backend"
echo "  - Log directory: /var/log/wildeditor"
echo "  - Port 8000 allowed through firewall"
echo ""

if [ "${NEED_RELOGIN:-false}" = "true" ]; then
    echo "⚠️  IMPORTANT: Please log out and back in for group changes to take effect!"
    echo "   Then test Docker with: docker run hello-world"
fi

echo ""
echo "🚀 Your server is now ready for Wildeditor Backend deployment!"

# Quick Development Setup - Local MCP + Remote Backend

**For developers who want to run MCP locally while using the production backend**

## 🚀 **Quick Start (5 minutes)**

### **1. Clone and Setup**
```bash
git clone https://github.com/LuminariMUD/wildeditor.git
cd wildeditor/apps/mcp

# Setup Python environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### **2. Configure Environment**
```bash
# Copy template
cp .env.example .env.development

# Edit .env.development with your settings:
```

```bash
# .env.development
NODE_ENV=development
MCP_PORT=8001
WILDEDITOR_MCP_KEY=dev-mcp-key-12345

# CHANGE THESE TO YOUR REMOTE BACKEND:
BACKEND_URL=https://your-backend-domain.com
WILDEDITOR_MCP_BACKEND_KEY=ask-jamie-for-this-key

# AI Configuration
OPENAI_API_KEY=your-openai-key
AI_SERVICE_PROVIDER=openai

# Development
LOG_LEVEL=DEBUG
ENABLE_DOCS=true
ENABLE_RELOAD=true
```

### **3. Test and Run**
```bash
# Test remote backend connection
curl -H "X-API-Key: your-mcp-backend-key" https://your-backend-domain.com/api/health

# Start MCP server
python -m src.main --env-file .env.development

# Test MCP server
curl http://localhost:8001/health
```

### **4. Verify Setup**
```bash
# MCP server should be running on http://localhost:8001
# API docs available at: http://localhost:8001/docs
# Backend connection test: http://localhost:8001/mcp/test-connection
```

## 🔧 **What This Gives You**

✅ **Local Development**: Hot reload, debugging, fast iteration  
✅ **Real Data**: Access to production wilderness data  
✅ **No Backend Setup**: No need to run MySQL or backend locally  
✅ **AI Testing**: Test AI tools with real spatial data  
✅ **Easy Debugging**: VS Code debugging, detailed logs  

## 🔍 **Common Issues**

**Connection Errors**: Check your MCP_BACKEND_KEY is correct  
**Port Conflicts**: Make sure port 8001 is available  
**API Key Issues**: Verify the key has proper permissions  

## 📞 **Need Help?**

- Check the full [Development Setup Guide](./DEVELOPMENT_SETUP.md)
- Review [Authentication Strategy](./AUTHENTICATION.md)  
- Ask Jamie for the MCP backend access key

---

**Time to setup**: ~5 minutes  
**Perfect for**: AI tool development, testing, rapid iteration

# Copilot Instructions for Luminari Wilderness Editor MCP Server

## 🎯 PROJECT CONTEXT

This is the **Luminari Wilderness Editor** project, a full-stack web application for creating and managing wilderness regions, paths, and landmarks for the LuminariMUD game. We are currently implementing an **MCP (Model Context Protocol) server** to add AI-powered capabilities.

## 📋 CURRENT PROJECT STATE

### **Implementation Status: PLANNING COMPLETE → READY FOR PHASE 1**
- ✅ **Planning Phase**: Complete with full documentation
- ⏳ **Phase 1 (Foundation)**: Ready to begin implementation
- ⏳ **Phase 2-6**: Planned but not started

### **Architecture Decision Made**
- **Same-server deployment** with multi-container setup
- **Separate API keys** for backend vs MCP operations
- **Hybrid development** support (local MCP + remote backend)

## 📂 KEY DOCUMENTATION TO REVIEW

**ALWAYS READ THESE FIRST when starting a new context:**

1. **`docs/mcp/MCP_IMPLEMENTATION_PLAN.md`** - Master implementation plan with 6 phases
2. **`docs/mcp/ARCHITECTURE.md`** - Complete technical architecture
3. **`docs/mcp/AUTHENTICATION.md`** - Multi-key authentication strategy
4. **`docs/mcp/DEPLOYMENT.md`** - Same-server deployment guide
5. **`docs/mcp/DEVELOPMENT_SETUP.md`** - Local development setup
6. **`.copilot/PROJECT_STATE.md`** - Current implementation status (THIS FILE SHOWS EXACTLY WHERE WE ARE)

## 🏗️ PROJECT STRUCTURE

```
wildeditor/
├── apps/
│   ├── frontend/           # Existing React frontend
│   ├── backend/           # Existing FastAPI backend (Port 8000)
│   └── mcp/              # NEW: MCP Server (Port 8001) - TO BE IMPLEMENTED
├── packages/
│   └── auth/             # NEW: Shared authentication - TO BE IMPLEMENTED
├── docs/mcp/             # ✅ Complete documentation
└── .copilot/             # ✅ Context files for AI assistants
```

## 🎯 NEXT STEPS (PHASE 1)

**Current Priority: Foundation Setup**

1. **Shared Authentication Package** (`packages/auth/`)
   - Extract API key auth from existing backend
   - Create reusable authentication package
   - Support multiple key types (backend, MCP, MCP-to-backend)

2. **Basic MCP Server Structure** (`apps/mcp/`)
   - FastAPI application setup
   - Health check endpoints
   - Basic MCP protocol implementation
   - Docker containerization

3. **Development Environment**
   - Local development setup
   - Hybrid development (local MCP + remote backend)
   - Testing framework

## 🔧 DEVELOPMENT APPROACH

### **Authentication Strategy**
- **Backend API Key**: `WILDEDITOR_API_KEY` (existing)
- **MCP Operations Key**: `WILDEDITOR_MCP_KEY` (new)
- **MCP-to-Backend Key**: `WILDEDITOR_MCP_BACKEND_KEY` (new)

### **Development Workflow**
- **Hybrid Development**: Run MCP locally, use remote backend
- **No local backend required** for MCP development
- **Real production data** for testing AI tools

## 📊 IMPLEMENTATION PHASES

1. **Phase 1: Foundation** (Week 1-2) ← **WE ARE HERE**
2. **Phase 2: Core Tools** (Week 2-3)
3. **Phase 3: Domain Knowledge** (Week 3-4)
4. **Phase 4: AI Prompts** (Week 4-5)
5. **Phase 5: Deployment** (Week 5-6)
6. **Phase 6: Testing** (Week 6-7)

## 🚨 IMPORTANT NOTES

### **DO NOT CHANGE EXISTING BACKEND**
- The backend (`apps/backend/`) is production code
- Only extract authentication code to shared package
- MCP server is completely separate service

### **FOLLOW ESTABLISHED PATTERNS**
- Use same FastAPI patterns as existing backend
- Follow existing code structure and naming
- Maintain compatibility with existing authentication

### **DEVELOPMENT PRIORITY**
- Get basic MCP server running first
- Focus on authentication integration
- Ensure hybrid development works

## 🔍 WHEN HELPING WITH IMPLEMENTATION

### **Always Check First:**
1. Read `.copilot/PROJECT_STATE.md` for current status
2. Review the specific phase documentation
3. Check existing backend code for patterns to follow
4. Verify changes don't break existing functionality

### **Code Quality Standards:**
- Follow existing Python style (Black, isort, flake8)
- Use type hints throughout
- Write comprehensive tests
- Document all public APIs

### **Testing Requirements:**
- Unit tests for all business logic
- Integration tests for MCP protocol
- Authentication tests for all key types
- Performance tests for AI operations

## 📞 GETTING CONTEXT

**If you need to understand the current state:**
1. Read `.copilot/PROJECT_STATE.md` (updated after each session)
2. Check recent git commits for progress
3. Review phase-specific documentation in `docs/mcp/`
4. Look at existing backend code for patterns

**If implementing new features:**
1. Check the implementation plan for that phase
2. Follow the architecture guidelines
3. Use existing backend patterns where possible
4. Update PROJECT_STATE.md when complete

## 🎯 SUCCESS CRITERIA

**Phase 1 Complete When:**
- [ ] Shared auth package working in both backend and MCP
- [ ] Basic MCP server responding to health checks
- [ ] Docker containers can communicate
- [ ] Local development environment setup working
- [ ] All tests passing

---

**Remember**: This is a well-planned project with complete documentation. Always refer to the docs first, and update PROJECT_STATE.md as you make progress so the next AI assistant knows exactly where things stand.

**Current Status**: Ready to begin Phase 1 implementation

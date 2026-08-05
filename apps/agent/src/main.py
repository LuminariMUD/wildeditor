"""Main FastAPI application for Chat Agent Service"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from routers import chat, session, health
from session.storage import create_storage
from session.manager import SessionManager
from agent.chat_agent import WildernessAssistantAgent
from services.mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
storage = None
session_manager = None
chat_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global storage, session_manager, chat_agent
    
    # Startup
    logger.info("Starting Chat Agent Service...")
    
    logger.info("Runtime configuration loaded")

    if (
        settings.wildeditor_environment == "remote-production"
        and settings.storage_backend != "redis"
    ):
        raise RuntimeError("Production chat sessions require Redis storage")
    
    # Initialize storage
    storage = create_storage(
        settings.storage_backend,
        redis_url=settings.redis_url,
        default_ttl=settings.session_ttl
    )
    
    # Initialize session manager
    session_manager = SessionManager(storage, settings.session_ttl)
    
    # Initialize MCP client
    mcp_client = MCPClient()
    
    # Initialize chat agent with MCP tools (single contact surface)
    try:
        chat_agent = WildernessAssistantAgent(mcp_client)
        logger.info("Chat agent initialized successfully with MCP tools")
    except Exception as e:
        logger.error("Chat agent initialization failed: %s", type(e).__name__)
        raise
    
    # Store in app state
    app.state.storage = storage
    app.state.session_manager = session_manager
    app.state.mcp_client = mcp_client
    app.state.chat_agent = chat_agent
    
    logger.info(f"Chat Agent Service started on port {settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Chat Agent Service...")
    
    # Clean up Redis connection if applicable
    if hasattr(storage, 'close'):
        await storage.close()
    
    logger.info("Chat Agent Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Wilderness Editor Chat Agent",
    description="AI-powered assistant for wilderness building in LuminariMUD",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(session.router, prefix="/api/session", tags=["Session"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Wilderness Editor Chat Agent",
        "version": "1.0.0",
        "status": "running",
        "port": settings.port,
        "model": f"{settings.model_provider}/{settings.model_name}",
        "storage": settings.storage_backend
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

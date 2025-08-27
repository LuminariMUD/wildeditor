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
from services.backend_client import BackendClient
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
    
    # Debug: Log environment variables
    import os
    logger.info("Environment variables check:")
    logger.info(f"MODEL_PROVIDER: {os.getenv('MODEL_PROVIDER', 'not set')}")
    logger.info(f"OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'} (len: {len(os.getenv('OPENAI_API_KEY', ''))})")
    logger.info(f"DEEPSEEK_API_KEY: {'set' if os.getenv('DEEPSEEK_API_KEY') else 'not set'} (len: {len(os.getenv('DEEPSEEK_API_KEY', ''))})")
    logger.info(f"Settings loaded - model_provider: {settings.model_provider}")
    logger.info(f"Settings loaded - openai_api_key: {'set' if settings.openai_api_key else 'not set'}")
    logger.info(f"Settings loaded - deepseek_api_key: {'set' if settings.deepseek_api_key else 'not set'}")
    
    # Initialize storage
    storage = create_storage(
        settings.storage_backend,
        redis_url=settings.redis_url,
        default_ttl=settings.session_ttl
    )
    
    # Initialize session manager
    session_manager = SessionManager(storage, settings.session_ttl)
    
    # Initialize service clients
    backend_client = BackendClient()
    mcp_client = MCPClient()
    
    # Initialize chat agent with tools
    try:
        chat_agent = WildernessAssistantAgent(backend_client, mcp_client)
        logger.info("Chat agent initialized successfully with MCP tools")
    except Exception as e:
        logger.error(f"Failed to initialize chat agent: {str(e)}")
        # Try without tools as fallback
        try:
            chat_agent = WildernessAssistantAgent()
            logger.warning("Chat agent initialized without MCP tools (fallback mode)")
        except Exception as e2:
            logger.error(f"Failed to initialize chat agent even without tools: {str(e2)}")
            raise
    
    # Store in app state
    app.state.storage = storage
    app.state.session_manager = session_manager
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
"""
Main FastAPI application for the MCP server
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from wildeditor_auth import AuthMiddleware

from .config import settings
from .routers import health, mcp_operations

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info(f"Starting Wildeditor MCP Server v1.0.1 on port {settings.mcp_port}")
    logger.info(f"Environment: {settings.node_env}")
    logger.info(f"Backend URL: {settings.backend_base_url}")
    logger.info(f"API Key configured: {'Yes' if settings.api_key else 'No'}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Wildeditor MCP Server")


# Create FastAPI application
app = FastAPI(
    title="Wildeditor MCP Server",
    description="Model Context Protocol server for AI-powered wilderness management",
    version="1.0.1",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(
    AuthMiddleware,
    exclude_paths={"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"},
    mcp_path_prefix="/mcp",
    backend_path_prefix="/api"  # Not used in MCP server but required for middleware
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(mcp_operations.router, prefix="/mcp", tags=["MCP Operations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.mcp_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )

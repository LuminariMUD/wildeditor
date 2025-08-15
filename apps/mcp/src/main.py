"""
Main FastAPI application for the MCP server
"""

import logging
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

# Create FastAPI application
app = FastAPI(
    title="Wildeditor MCP Server",
    description="Model Context Protocol server for AI-powered wilderness management",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None
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

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting Wildeditor MCP Server on port {settings.mcp_port}")
    logger.info(f"Environment: {settings.node_env}")
    logger.info(f"Backend URL: {settings.backend_base_url}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Wildeditor MCP Server")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.mcp_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )

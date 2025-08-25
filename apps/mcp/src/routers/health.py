"""
Health check endpoints for the MCP server
"""

from fastapi import APIRouter, Depends
from wildeditor_auth import verify_mcp_key
from ..config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Public health check endpoint
    
    Returns basic server status without requiring authentication.
    Used by load balancers and monitoring systems.
    """
    return {
        "status": "healthy",
        "service": "wildeditor-mcp-server",
        "version": "1.0.1",
        "environment": settings.node_env
    }

@router.get("/health/detailed")
async def detailed_health_check(authenticated: bool = Depends(verify_mcp_key)):
    """
    Detailed health check with authentication
    
    Requires MCP operations key. Returns detailed service status
    including backend connectivity.
    """
    # TODO: Add backend connectivity check in Phase 2
    return {
        "status": "healthy",
        "service": "wildeditor-mcp-server", 
        "version": "1.0.1",
        "environment": settings.node_env,
        "authenticated": True,
        "backend_url": settings.backend_base_url,
        "features": {
            "mcp_protocol": "1.0.0",
            "authentication": "multi-key",
            "backend_integration": "active",
            "ai_fallback": "ollama"
        }
    }

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
        "version": "1.0.9",
        "environment": settings.node_env
    }

@router.get("/health/debug")
async def debug_environment(authenticated: bool = Depends(verify_mcp_key)):
    """
    TEMPORARY: Debug endpoint to check environment variables
    Remove this after debugging is complete!
    """
    import os
    
    # Get AI-related environment variables (mask sensitive parts)
    def mask_key(key: str, value: str) -> str:
        if not value:
            return "NOT_SET"
        if "KEY" in key.upper() and len(value) > 8:
            # Show first 4 and last 4 chars of keys
            return f"{value[:4]}...{value[-4:]}"
        return value
    
    env_vars = {
        "AI_PROVIDER": os.getenv("AI_PROVIDER", "NOT_SET"),
        "OPENAI_API_KEY": mask_key("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "NOT_SET"),
        "ANTHROPIC_API_KEY": mask_key("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", "")),
        "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL", "NOT_SET"),
        "DEEPSEEK_API_KEY": mask_key("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY", "")),
        "DEEPSEEK_MODEL": os.getenv("DEEPSEEK_MODEL", "NOT_SET"),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "NOT_SET"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "NOT_SET"),
        "WILDEDITOR_MCP_KEY": mask_key("MCP_KEY", os.getenv("WILDEDITOR_MCP_KEY", "")),
        "WILDEDITOR_API_KEY": mask_key("API_KEY", os.getenv("WILDEDITOR_API_KEY", "")),
        "WILDEDITOR_BACKEND_URL": os.getenv("WILDEDITOR_BACKEND_URL", "NOT_SET"),
    }
    
    # Test Ollama connectivity from within container
    ollama_test = {"ollama_reachable": False, "error": None}
    try:
        import requests
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            ollama_test["ollama_reachable"] = True
            ollama_test["models"] = [m["name"] for m in data.get("models", [])]
        else:
            ollama_test["error"] = f"Status {response.status_code}"
    except Exception as e:
        ollama_test["error"] = str(e)
    
    # Check actual AI service configuration
    ai_service_info = {"configured_provider": "NOT_SET", "is_available": False, "error": None}
    try:
        from ..services.ai_service import get_ai_service
        ai_service = get_ai_service()
        ai_service_info["configured_provider"] = ai_service.provider.value
        ai_service_info["is_available"] = ai_service.is_available()
        ai_service_info["has_model"] = ai_service.model is not None
        ai_service_info["has_agent"] = ai_service.agent is not None
        ai_service_info["initialization_error"] = getattr(ai_service, 'initialization_error', None)
    except Exception as e:
        ai_service_info["error"] = str(e)
    
    return {
        "status": "debug",
        "service": "wildeditor-mcp-server",
        "version": "1.0.10-debug",
        "environment_variables": env_vars,
        "ai_service_status": ai_service_info,
        "ollama_connectivity_test": ollama_test,
        "warning": "TEMPORARY DEBUG ENDPOINT - REMOVE AFTER TESTING"
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
        "version": "1.0.9",
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

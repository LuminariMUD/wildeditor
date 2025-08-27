"""Health check endpoints"""
from fastapi import APIRouter, Request
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check(request: Request):
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "Chat Agent",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(request: Request):
    """
    Readiness check
    
    Verifies that all components are initialized and ready.
    """
    try:
        # Check if components are initialized
        checks = {
            "storage": hasattr(request.app.state, 'storage') and request.app.state.storage is not None,
            "session_manager": hasattr(request.app.state, 'session_manager') and request.app.state.session_manager is not None,
            "chat_agent": hasattr(request.app.state, 'chat_agent') and request.app.state.chat_agent is not None
        }
        
        all_ready = all(checks.values())
        
        return {
            "ready": all_ready,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/live")
async def liveness_check():
    """
    Liveness check
    
    Simple check to verify the service is running.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
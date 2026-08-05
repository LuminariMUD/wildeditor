"""Health check endpoints"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import UTC, datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check(request: Request):
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "Chat Agent",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(request: Request):
    """
    Readiness check
    
    Verify initialized components and their external dependencies.
    """
    try:
        storage = getattr(request.app.state, "storage", None)
        mcp_client = getattr(request.app.state, "mcp_client", None)
        checks = {
            "storage": storage is not None and await storage.ping(),
            "mcp": mcp_client is not None and await mcp_client.health_check(),
            "session_manager": getattr(request.app.state, "session_manager", None) is not None,
            "chat_agent": getattr(request.app.state, "chat_agent", None) is not None,
        }
        all_ready = all(checks.values())

        return JSONResponse(
            status_code=200 if all_ready else 503,
            content={
                "ready": all_ready,
                "checks": checks,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    except Exception as exc:
        logger.error("Readiness check failed: %s", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "error": "Readiness check failed",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )


@router.get("/live")
async def liveness_check():
    """
    Liveness check
    
    Simple check to verify the service is running.
    """
    return {
        "alive": True,
        "timestamp": datetime.now(UTC).isoformat()
    }

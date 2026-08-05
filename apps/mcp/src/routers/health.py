"""Health check endpoints for the MCP server."""

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from wildeditor_auth import verify_mcp_key

from ..audit import backend_request_headers
from ..config import settings


router = APIRouter()


async def backend_is_ready() -> bool:
    """Verify that MCP can authenticate to the backend service boundary."""

    if not settings.backend_service_key:
        return False
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.backend_base_url}/auth/status",
                headers=backend_request_headers(),
                timeout=3.0,
            )
    except httpx.HTTPError:
        return False

    if response.status_code != 200:
        return False
    try:
        payload = response.json()
    except ValueError:
        return False
    return (
        payload.get("authenticated") is True
        and payload.get("kind") == "service"
        and payload.get("role") == "service"
    )


@router.get("/health")
async def health_check():
    """Return public liveness without configuration or credential details."""

    return {
        "status": "healthy",
        "service": "wildeditor-mcp-server",
        "version": "1.0.10",
        "environment": settings.node_env,
    }


@router.get("/health/detailed")
async def detailed_health_check(
    authenticated: bool = Depends(verify_mcp_key),
):
    """Return authenticated readiness without echoing secret values."""

    backend_ready = await backend_is_ready()
    return JSONResponse(
        status_code=200 if backend_ready else 503,
        content={
            "status": "healthy" if backend_ready else "unavailable",
            "ready": backend_ready,
            "service": "wildeditor-mcp-server",
            "version": "1.0.10",
            "environment": settings.node_env,
            "authenticated": authenticated,
            "checks": {
                "backend_service_auth": backend_ready,
            },
            "features": {
                "mcp_protocol": "1.0.0",
                "authentication": "service-boundary",
                "backend_integration": "active" if backend_ready else "unavailable",
            },
        },
    )

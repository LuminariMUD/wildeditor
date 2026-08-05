"""Trusted request context and backend authentication for MCP calls."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings


@dataclass(frozen=True)
class AuditContext:
    actor: str
    request_id: str


_audit_context: ContextVar[AuditContext | None] = ContextVar(
    "mcp_audit_context",
    default=None,
)


def _safe_header(value: str | None, fallback: str) -> str:
    if not value or len(value) > 200 or any(ord(character) < 32 for character in value):
        return fallback
    return value


class AuditContextMiddleware(BaseHTTPMiddleware):
    """Bind internal headers for the lifetime of one MCP request."""

    async def dispatch(self, request: Request, call_next):
        context = AuditContext(
            actor=_safe_header(
                request.headers.get("X-Wildeditor-Actor"),
                "mcp-service",
            ),
            request_id=_safe_header(
                request.headers.get("X-Wildeditor-Request-ID"),
                "mcp-service-request",
            ),
        )
        token: Token[AuditContext | None] = _audit_context.set(context)
        try:
            return await call_next(request)
        finally:
            _audit_context.reset(token)


def backend_request_headers() -> dict[str, str]:
    """Build server-only backend headers with trusted audit context."""

    if not settings.backend_service_key:
        raise RuntimeError("WILDEDITOR_BACKEND_SERVICE_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {settings.backend_service_key}",
    }
    context = _audit_context.get()
    if context:
        headers["X-Wildeditor-Actor"] = context.actor
        headers["X-Wildeditor-Request-ID"] = context.request_id
    return headers

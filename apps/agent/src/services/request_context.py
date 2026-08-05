"""Request-scoped, server-derived audit context for MCP calls."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass

from wildeditor_auth import Principal


@dataclass(frozen=True)
class RequestContext:
    actor: str
    role: str
    request_id: str


current_request_context: ContextVar[RequestContext | None] = ContextVar(
    "wildeditor_request_context",
    default=None,
)


def bind_request_context(
    principal: Principal,
    request_id: str,
) -> Token[RequestContext | None]:
    return current_request_context.set(
        RequestContext(
            actor=principal.subject,
            role=principal.role.value,
            request_id=request_id,
        )
    )


def reset_request_context(token: Token[RequestContext | None]) -> None:
    current_request_context.reset(token)

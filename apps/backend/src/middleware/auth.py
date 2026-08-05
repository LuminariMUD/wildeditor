"""Human JWT and server-to-server authentication for the backend API."""

from __future__ import annotations

import os
import uuid
from typing import Iterable, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from wildeditor_auth import (
    BearerAuthenticator,
    DEVELOPMENT_PRINCIPAL,
    JWTIssuer,
    JWTVerifier,
    Principal,
    PrincipalKind,
    PrincipalRole,
    TokenValidationError,
)


security = HTTPBearer(auto_error=False)

_authenticator: Optional[BearerAuthenticator] = None
_authenticator_signature: Optional[tuple[str, ...]] = None


def is_auth_required() -> bool:
    """Authentication may only be bypassed in explicit local development."""

    requested_bypass = os.getenv("REQUIRE_AUTH", "true").lower() in {
        "false",
        "0",
        "no",
    }
    environment = os.getenv("WILDEDITOR_ENVIRONMENT", "local-development")
    return not (requested_bypass and environment == "local-development")


def _csv_env(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def _auth_environment_signature() -> tuple[str, ...]:
    names = (
        "WILDEDITOR_AUTH_ISSUERS",
        "WILDEDITOR_AUTH_JWKS_URLS",
        "WILDEDITOR_AUTH_AUDIENCE",
        "WILDEDITOR_AUTH_ALLOWED_ALGORITHMS",
        "WILDEDITOR_AUTH_JWKS_CACHE_TTL",
        "WILDEDITOR_BACKEND_SERVICE_KEY",
    )
    return tuple(os.getenv(name, "") for name in names)


def _build_authenticator() -> BearerAuthenticator:
    issuer_names = _csv_env("WILDEDITOR_AUTH_ISSUERS")
    if not issuer_names:
        raise ValueError("WILDEDITOR_AUTH_ISSUERS is not configured")

    jwks_urls = _csv_env("WILDEDITOR_AUTH_JWKS_URLS")
    if jwks_urls and len(jwks_urls) != len(issuer_names):
        raise ValueError(
            "WILDEDITOR_AUTH_JWKS_URLS must have one entry per trusted issuer"
        )

    audience = os.getenv("WILDEDITOR_AUTH_AUDIENCE", "authenticated").strip()
    issuers = [
        JWTIssuer(
            issuer=issuer,
            jwks_url=(jwks_urls[index] if jwks_urls else f"{issuer.rstrip('/')}/.well-known/jwks.json"),
            audience=audience,
        )
        for index, issuer in enumerate(issuer_names)
    ]

    algorithms = _csv_env("WILDEDITOR_AUTH_ALLOWED_ALGORITHMS", "ES256")
    cache_ttl = int(os.getenv("WILDEDITOR_AUTH_JWKS_CACHE_TTL", "300"))
    verifier = JWTVerifier(
        issuers,
        allowed_algorithms=algorithms,
        cache_ttl_seconds=cache_ttl,
    )
    return BearerAuthenticator(
        verifier,
        service_key=os.getenv("WILDEDITOR_BACKEND_SERVICE_KEY"),
        service_subject="mcp",
    )


def get_authenticator() -> BearerAuthenticator:
    """Reuse the verifier cache while rebuilding safely after env changes in tests."""

    global _authenticator, _authenticator_signature
    signature = _auth_environment_signature()
    if _authenticator is None or signature != _authenticator_signature:
        _authenticator = _build_authenticator()
        _authenticator_signature = signature
    return _authenticator


async def verify_principal(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Principal:
    """Authenticate the caller and return its typed principal."""

    if not is_auth_required():
        principal = DEVELOPMENT_PRINCIPAL
    else:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            authenticator = get_authenticator()
            principal = await authenticator.authenticate(credentials.credentials)
        except TokenValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication is not configured on the server.",
            ) from exc

    if principal.kind is PrincipalKind.SERVICE:
        request.state.audit_actor = _safe_internal_header(
            request.headers.get("X-Wildeditor-Actor"),
            principal.subject,
        )
        request.state.audit_request_id = _safe_internal_header(
            request.headers.get("X-Wildeditor-Request-ID"),
            str(uuid.uuid4()),
        )
    else:
        # Browser-supplied identity/request headers are not trusted.
        request.state.audit_actor = principal.subject
        request.state.audit_request_id = str(uuid.uuid4())
    return principal


def _safe_internal_header(value: Optional[str], fallback: str) -> str:
    if not value or len(value) > 200 or any(ord(character) < 32 for character in value):
        return fallback
    return value


def require_roles(
    roles: Iterable[PrincipalRole],
    *,
    human_only: bool = False,
):
    """Create a dependency that returns 403 for a valid but unauthorized caller."""

    allowed = frozenset(roles)

    async def dependency(
        principal: Principal = Depends(verify_principal),
    ) -> Principal:
        if human_only and principal.kind is PrincipalKind.SERVICE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation requires a human principal.",
            )
        if principal.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return principal

    return dependency


require_reader = require_roles(
    {
        PrincipalRole.VIEWER,
        PrincipalRole.EDITOR,
        PrincipalRole.ADMIN,
        PrincipalRole.SERVICE,
    }
)
require_editor = require_roles(
    {PrincipalRole.EDITOR, PrincipalRole.ADMIN, PrincipalRole.SERVICE}
)
require_human_editor = require_roles(
    {PrincipalRole.EDITOR, PrincipalRole.ADMIN},
    human_only=True,
)
require_admin = require_roles({PrincipalRole.ADMIN}, human_only=True)

# FastAPI default-value aliases retained for concise router signatures.
RequireReader = Depends(require_reader)
RequireEditor = Depends(require_editor)
RequireHumanEditor = Depends(require_human_editor)
RequireAdmin = Depends(require_admin)

# Transitional import alias. New code should select an explicit permission.
verify_api_key = verify_principal
RequireAuth = RequireReader

"""JWT authentication dependencies for browser-facing chat routes."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from wildeditor_auth import (
    BearerAuthenticator,
    DEVELOPMENT_PRINCIPAL,
    JWTIssuer,
    JWTVerifier,
    Principal,
    PrincipalRole,
    TokenValidationError,
)


security = HTTPBearer(auto_error=False)
_authenticator: Optional[BearerAuthenticator] = None
_signature: Optional[tuple[str, ...]] = None


def _csv_env(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def _environment_signature() -> tuple[str, ...]:
    names = (
        "WILDEDITOR_AUTH_ISSUERS",
        "WILDEDITOR_AUTH_JWKS_URLS",
        "WILDEDITOR_AUTH_AUDIENCE",
        "WILDEDITOR_AUTH_ALLOWED_ALGORITHMS",
        "WILDEDITOR_AUTH_JWKS_CACHE_TTL",
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
    verifier = JWTVerifier(
        issuers,
        allowed_algorithms=_csv_env(
            "WILDEDITOR_AUTH_ALLOWED_ALGORITHMS",
            "ES256",
        ),
        cache_ttl_seconds=int(
            os.getenv("WILDEDITOR_AUTH_JWKS_CACHE_TTL", "300")
        ),
    )
    # The browser-facing agent never accepts a service credential.
    return BearerAuthenticator(verifier)


def get_authenticator() -> BearerAuthenticator:
    global _authenticator, _signature
    signature = _environment_signature()
    if _authenticator is None or signature != _signature:
        _authenticator = _build_authenticator()
        _signature = signature
    return _authenticator


def _development_bypass_enabled() -> bool:
    auth_disabled = os.getenv("REQUIRE_AUTH", "true").lower() in {
        "false",
        "0",
        "no",
    }
    environment = os.getenv("WILDEDITOR_ENVIRONMENT", "local-development")
    return auth_disabled and environment == "local-development"


async def require_human_editor(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Principal:
    """Require a verified editor/admin JWT; return 403 for lower roles."""

    if _development_bypass_enabled():
        return DEVELOPMENT_PRINCIPAL

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        principal = await get_authenticator().authenticate(
            credentials.credentials,
            allow_service=False,
        )
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

    if principal.role not in {PrincipalRole.EDITOR, PrincipalRole.ADMIN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat requires the editor role.",
        )
    return principal

"""
Wildeditor Shared Authentication Package

This package provides multi-key authentication support for both the
Wildeditor backend API and MCP server, ensuring consistent security
across all services.
"""

from .api_key import MultiKeyAuth, KeyType
from .exceptions import AuthenticationError
from .middleware import AuthMiddleware
from .dependencies import verify_mcp_key
from .bearer import BearerAuthenticator
from .jwt_verifier import JWTIssuer, JWTVerifier, TokenValidationError
from .principal import (
    DEVELOPMENT_PRINCIPAL,
    Principal,
    PrincipalKind,
    PrincipalRole,
)

__version__ = "2.0.0"
__all__ = [
    "MultiKeyAuth",
    "KeyType",
    "AuthenticationError",
    "AuthMiddleware",
    "verify_mcp_key",
    "BearerAuthenticator",
    "JWTIssuer",
    "JWTVerifier",
    "TokenValidationError",
    "DEVELOPMENT_PRINCIPAL",
    "Principal",
    "PrincipalKind",
    "PrincipalRole",
]

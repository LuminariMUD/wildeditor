"""
Wildeditor Shared Authentication Package

This package provides multi-key authentication support for both the 
Wildeditor backend API and MCP server, ensuring consistent security
across all services.
"""

from .api_key import MultiKeyAuth, KeyType
from .exceptions import AuthenticationError
from .middleware import AuthMiddleware
from .dependencies import verify_api_key, verify_mcp_key, verify_backend_access_key

__version__ = "1.0.0"
__all__ = [
    "MultiKeyAuth",
    "KeyType", 
    "AuthenticationError",
    "AuthMiddleware",
    "verify_api_key",
    "verify_mcp_key",
    "verify_backend_access_key"
]

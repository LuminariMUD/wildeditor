"""
FastAPI dependency functions for authentication
"""

from typing import Optional
from fastapi import Header, Depends
from .api_key import MultiKeyAuth, KeyType


# Global auth instance
auth_instance = MultiKeyAuth()


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify backend API key"""
    return auth_instance.verify_key(x_api_key, KeyType.BACKEND_API)


async def verify_mcp_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify MCP operations key"""
    return auth_instance.verify_key(x_api_key, KeyType.MCP_OPERATIONS)


async def verify_backend_access_key(
        x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify MCP backend access key"""
    return auth_instance.verify_key(x_api_key, KeyType.MCP_BACKEND_ACCESS)


def get_auth_dependency(key_type: KeyType):
    """
    Factory function to create auth dependencies for specific key types

    Args:
        key_type: The type of key to verify

    Returns:
        FastAPI dependency function
    """
    async def verify_key_dependency(
            x_api_key: Optional[str] = Header(None)) -> bool:
        return auth_instance.verify_key(x_api_key, key_type)

    return verify_key_dependency


# Convenience dependencies for common use cases
RequireBackendKey = Depends(verify_api_key)
RequireMCPKey = Depends(verify_mcp_key)
RequireBackendAccessKey = Depends(verify_backend_access_key)

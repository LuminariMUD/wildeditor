"""
Authentication middleware for Wildeditor API.

Provides simple API key-based authentication for administrators and builders.
"""

import os
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Initialize HTTP Bearer token security
security = HTTPBearer(auto_error=False)

def get_api_key_from_env() -> Optional[str]:
    """Get the API key from environment variables."""
    return os.getenv("WILDEDITOR_API_KEY")

def is_auth_required() -> bool:
    """Check if authentication is required based on environment."""
    # Default to requiring auth, can be disabled for development
    return os.getenv("REQUIRE_AUTH", "true").lower() in ("true", "1", "yes")

async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> bool:
    """
    Verify API key from Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        bool: True if authentication is valid or not required
        
    Raises:
        HTTPException: If authentication is required but invalid
    """
    # Check if auth is required
    if not is_auth_required():
        return True
    
    # Get the expected API key
    expected_api_key = get_api_key_from_env()
    
    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server. Please contact administrator."
        )
    
    # Check if credentials were provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide API key in Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the API key
    if credentials.credentials != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True

# Dependency for endpoints that require authentication
RequireAuth = Depends(verify_api_key)

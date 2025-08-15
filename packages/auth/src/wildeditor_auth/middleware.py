"""
FastAPI middleware for automatic authentication
"""

import json
from typing import Set, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .api_key import MultiKeyAuth, KeyType
from .exceptions import AuthenticationError


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically authenticate requests based on path
    """
    
    def __init__(
        self, 
        app, 
        exclude_paths: Optional[Set[str]] = None,
        mcp_path_prefix: str = "/mcp",
        backend_path_prefix: str = "/api"
    ):
        """
        Initialize auth middleware
        
        Args:
            app: FastAPI application
            exclude_paths: Paths to exclude from authentication
            mcp_path_prefix: Path prefix for MCP endpoints
            backend_path_prefix: Path prefix for backend endpoints
        """
        super().__init__(app)
        self.auth = MultiKeyAuth()
        self.exclude_paths = exclude_paths or {
            "/health", 
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/favicon.ico"
        }
        self.mcp_path_prefix = mcp_path_prefix
        self.backend_path_prefix = backend_path_prefix
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication"""
        
        # Skip authentication for excluded paths
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        
        # Determine required key type based on path
        key_type = self._determine_key_type(request.url.path)
        
        if key_type is None:
            # Path doesn't require authentication
            return await call_next(request)
        
        # Verify authentication
        try:
            self.auth.verify_key(api_key, key_type)
        except AuthenticationError as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        
        # Continue with authenticated request
        response = await call_next(request)
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from authentication"""
        return any(path.startswith(excluded) or path == excluded 
                  for excluded in self.exclude_paths)
    
    def _determine_key_type(self, path: str) -> Optional[KeyType]:
        """
        Determine required key type based on request path
        
        Args:
            path: Request path
            
        Returns:
            Required KeyType or None if no auth needed
        """
        if path.startswith(self.mcp_path_prefix):
            return KeyType.MCP_OPERATIONS
        elif path.startswith(self.backend_path_prefix):
            return KeyType.BACKEND_API
        
        # Default to no authentication required
        return None

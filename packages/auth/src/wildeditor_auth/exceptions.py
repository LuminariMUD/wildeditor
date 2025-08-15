"""
Custom exceptions for authentication failures
"""

from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Base authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail
        )


class InvalidAPIKeyError(AuthenticationError):
    """Raised when an invalid API key is provided"""
    def __init__(self, key_type: str = "API"):
        super().__init__(detail=f"Invalid {key_type} key")


class MissingAPIKeyError(AuthenticationError):
    """Raised when no API key is provided"""
    def __init__(self):
        super().__init__(detail="Missing API key in X-API-Key header")


class UnauthorizedKeyTypeError(AuthenticationError):
    """Raised when wrong key type is used for an endpoint"""
    def __init__(self, required_type: str, provided_type: str = "unknown"):
        super().__init__(
            detail=f"Unauthorized: {required_type} key required, {provided_type} provided"
        )

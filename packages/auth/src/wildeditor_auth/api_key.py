"""
Multi-key authentication system for Wildeditor services
"""

import os
from enum import Enum
from typing import Set, Optional, Dict
from .exceptions import InvalidAPIKeyError, MissingAPIKeyError


class KeyType(Enum):
    """Available API key types"""
    BACKEND_API = "backend_api"
    MCP_OPERATIONS = "mcp_operations"
    MCP_BACKEND_ACCESS = "mcp_backend_access"


class MultiKeyAuth:
    """
    Multi-key authentication handler supporting three key types:
    - BACKEND_API: For direct backend API access
    - MCP_OPERATIONS: For MCP server operations
    - MCP_BACKEND_ACCESS: For MCP server to access backend
    """

    def __init__(self):
        """Initialize with environment variables"""
        self.keys: Dict[KeyType, Set[str]] = {
            KeyType.BACKEND_API: {os.getenv("WILDEDITOR_API_KEY", "")},
            KeyType.MCP_OPERATIONS: {os.getenv("WILDEDITOR_MCP_KEY", "")},
            KeyType.MCP_BACKEND_ACCESS: {
                os.getenv("WILDEDITOR_MCP_BACKEND_KEY", "")
            }
        }

        # Remove empty keys
        for key_type in self.keys:
            self.keys[key_type] = {key for key in self.keys[key_type] if key}

    def is_valid_key(self, api_key: str, key_type: KeyType) -> bool:
        """Check if an API key is valid for the given key type"""
        if not api_key:
            return False
        return api_key in self.keys.get(key_type, set())

    def verify_key(self, api_key: Optional[str], key_type: KeyType) -> bool:
        """
        Verify an API key for the given key type

        Args:
            api_key: The API key to verify
            key_type: The type of key expected

        Returns:
            True if valid

        Raises:
            MissingAPIKeyError: If no key provided
            InvalidAPIKeyError: If key is invalid
        """
        if not api_key:
            raise MissingAPIKeyError()

        if not self.is_valid_key(api_key, key_type):
            raise InvalidAPIKeyError(key_type.value)

        return True

    def add_key(self, api_key: str, key_type: KeyType) -> None:
        """Add a new API key for the given type"""
        if api_key:
            self.keys[key_type].add(api_key)

    def remove_key(self, api_key: str, key_type: KeyType) -> None:
        """Remove an API key for the given type"""
        self.keys[key_type].discard(api_key)

    def get_key_count(self, key_type: KeyType) -> int:
        """Get the number of valid keys for a given type"""
        return len(self.keys.get(key_type, set()))

    def has_valid_keys(self, key_type: KeyType) -> bool:
        """Check if there are any valid keys for the given type"""
        return self.get_key_count(key_type) > 0

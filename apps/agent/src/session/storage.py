"""Session storage implementations for chat agent"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
import logging
from datetime import UTC, datetime, timedelta
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class SessionStorage(ABC):
    """Abstract base class for session storage backends"""
    
    @abstractmethod
    async def save(self, key: str, data: Dict[str, Any], ttl: int) -> None:
        """Save session data with TTL"""
        pass
    
    @abstractmethod
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load session data"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete session data"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if session exists"""
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """Return whether the storage dependency is reachable."""
        pass
    
    @abstractmethod
    async def extend_ttl(self, key: str, ttl: int) -> None:
        """Extend session TTL"""
        pass


class InMemoryStorage(SessionStorage):
    """In-memory session storage for development"""
    
    def __init__(self, default_ttl: int = 86400):
        """
        Initialize in-memory storage
        
        Args:
            default_ttl: Default TTL in seconds (24 hours)
        """
        self.store: Dict[str, Dict[str, Any]] = {}
        self.expiry: Dict[str, datetime] = {}
        self.default_ttl = default_ttl
        logger.info("Initialized InMemoryStorage")
    
    async def save(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Save session data with TTL"""
        ttl = ttl or self.default_ttl
        self.store[key] = data
        self.expiry[key] = datetime.now(UTC) + timedelta(seconds=ttl)
        logger.debug(f"Saved session {key} with TTL {ttl}s")
    
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load session data"""
        # Check expiry
        if key in self.expiry:
            if datetime.now(UTC) > self.expiry[key]:
                # Expired, clean up
                await self.delete(key)
                return None
        
        return self.store.get(key)
    
    async def delete(self, key: str) -> None:
        """Delete session data"""
        self.store.pop(key, None)
        self.expiry.pop(key, None)
        logger.debug(f"Deleted session {key}")
    
    async def exists(self, key: str) -> bool:
        """Check if session exists"""
        data = await self.load(key)
        return data is not None

    async def ping(self) -> bool:
        """In-memory storage is ready once constructed."""
        return True
    
    async def extend_ttl(self, key: str, ttl: int) -> None:
        """Extend session TTL"""
        if key in self.store:
            self.expiry[key] = datetime.now(UTC) + timedelta(seconds=ttl)
            logger.debug(f"Extended TTL for session {key} by {ttl}s")


class RedisStorage(SessionStorage):
    """Redis-based session storage for production"""
    
    def __init__(self, redis_url: str, default_ttl: int = 86400):
        """
        Initialize Redis storage
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
        """
        import redis.asyncio as redis
        
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = default_ttl
        logger.info("Initialized Redis session storage")
    
    async def save(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Save session data with TTL"""
        ttl = ttl or self.default_ttl
        try:
            json_data = json.dumps(data)
            await self.redis.set(key, json_data, ex=ttl)
            logger.debug(f"Saved session {key} to Redis with TTL {ttl}s")
        except Exception as exc:
            logger.error("Failed to save a Redis session (%s)", type(exc).__name__)
            raise
    
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load session data"""
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:
            logger.error("Failed to load a Redis session (%s)", type(exc).__name__)
            return None
    
    async def delete(self, key: str) -> None:
        """Delete session data"""
        try:
            await self.redis.delete(key)
            logger.debug(f"Deleted session {key} from Redis")
        except Exception as exc:
            logger.error("Failed to delete a Redis session (%s)", type(exc).__name__)
    
    async def exists(self, key: str) -> bool:
        """Check if session exists"""
        try:
            exists = await self.redis.exists(key)
            return bool(exists)
        except Exception as exc:
            logger.error("Failed to check a Redis session (%s)", type(exc).__name__)
            return False

    async def ping(self) -> bool:
        """Check Redis connectivity without exposing connection details."""
        try:
            return bool(await self.redis.ping())
        except Exception as exc:
            logger.error("Redis readiness check failed (%s)", type(exc).__name__)
            return False
    
    async def extend_ttl(self, key: str, ttl: int) -> None:
        """Extend session TTL"""
        try:
            await self.redis.expire(key, ttl)
            logger.debug(f"Extended TTL for session {key} by {ttl}s")
        except Exception as exc:
            logger.error("Failed to extend a Redis session TTL (%s)", type(exc).__name__)
    
    async def close(self) -> None:
        """Close Redis connection"""
        await self.redis.aclose()


def create_storage(backend: str = "memory", **kwargs) -> SessionStorage:
    """
    Factory function to create storage backend
    
    Args:
        backend: Storage backend type ('memory' or 'redis')
        **kwargs: Additional arguments for the storage backend
        
    Returns:
        SessionStorage instance
    """
    if backend == "redis":
        redis_url = kwargs.get("redis_url") or "redis://localhost:6379"
        return RedisStorage(redis_url, kwargs.get("default_ttl", 86400))
    if backend == "memory":
        return InMemoryStorage(kwargs.get("default_ttl", 86400))
    raise ValueError("Unsupported session storage backend")

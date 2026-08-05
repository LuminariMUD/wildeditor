"""Real Redis integration for production chat session storage."""

import os
from uuid import uuid4

import pytest

from session.storage import RedisStorage


@pytest.mark.asyncio
async def test_redis_storage_round_trip_ttl_and_close():
    redis_url = os.getenv("TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("TEST_REDIS_URL is not configured")

    storage = RedisStorage(redis_url, default_ttl=60)
    key = f"wildeditor:test:{uuid4()}"
    try:
        assert await storage.ping() is True
        await storage.save(key, {"owner": "verified-subject"}, ttl=30)
        assert await storage.load(key) == {"owner": "verified-subject"}
        assert await storage.exists(key) is True

        await storage.extend_ttl(key, 45)
        remaining_ttl = await storage.redis.ttl(key)
        assert 0 < remaining_ttl <= 45

        await storage.delete(key)
        assert await storage.exists(key) is False
    finally:
        await storage.delete(key)
        await storage.close()

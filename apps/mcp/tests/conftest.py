import pytest
import asyncio
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client"""
    # We'll import here to avoid import issues during package setup
    from src.main import app
    return TestClient(app)


@pytest.fixture
def mcp_headers():
    """Headers for MCP operations"""
    return {"X-API-Key": "test-mcp-key"}


@pytest.fixture
def invalid_headers():
    """Invalid headers for testing"""
    return {"X-API-Key": "invalid-key"}

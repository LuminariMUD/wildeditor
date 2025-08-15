import pytest
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add the mcp directory to Python path so we can import src module
current_dir = Path(__file__).parent  # tests/
mcp_dir = current_dir.parent         # apps/mcp/
sys.path.insert(0, str(mcp_dir))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Set up test environment for the entire session
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables for all tests"""
    test_env = {
        "WILDEDITOR_MCP_KEY": "test-mcp-key",
        "WILDEDITOR_API_KEY": "test-backend-key"
    }
    
    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture
def client(setup_test_env):
    """Create test client with proper environment setup"""
    # Import here so the app gets the patched environment
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

import pytest
import asyncio
import os
from unittest.mock import patch


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    env_vars = {
        "WILDEDITOR_API_KEY": "test-backend-key",
        "WILDEDITOR_MCP_KEY": "test-mcp-key", 
        "WILDEDITOR_MCP_BACKEND_KEY": "test-mcp-backend-key"
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def valid_backend_key():
    return "test-backend-key"


@pytest.fixture
def valid_mcp_key():
    return "test-mcp-key"


@pytest.fixture
def valid_mcp_backend_key():
    return "test-mcp-backend-key"


@pytest.fixture
def invalid_key():
    return "invalid-key-value"

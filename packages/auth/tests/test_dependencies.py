import pytest
from fastapi import FastAPI  # HTTPException not used, removing
from fastapi.testclient import TestClient
from wildeditor_auth.dependencies import (
    get_auth_dependency,
    RequireMCPKey,
    auth_instance
)
from wildeditor_auth.api_key import KeyType


def create_test_app():
    """Create test app with fresh auth instance"""
    app = FastAPI()

    @app.get("/test-mcp")
    async def test_mcp_endpoint(authenticated: bool = RequireMCPKey):
        return {
            "message": "MCP access granted",
            "authenticated": authenticated}

    return app


@pytest.fixture
def app(mock_env):
    """Create test app with mocked environment"""
    # Reinitialize auth instance with mocked environment
    from wildeditor_auth.api_key import MultiKeyAuth
    auth_instance.__dict__.update(MultiKeyAuth().__dict__)
    return create_test_app()


@pytest.fixture
def client(app):
    return TestClient(app)


class TestDependencies:
    """Test cases for authentication dependencies"""

    def test_mcp_auth_success(self, client, mock_env, valid_mcp_key):
        """Test successful MCP authentication"""
        headers = {"X-API-Key": valid_mcp_key}
        response = client.get("/test-mcp", headers=headers)

        assert response.status_code == 200
        assert response.json()["authenticated"] is True

    def test_mcp_auth_failure(self, client, mock_env, invalid_key):
        """Test MCP authentication failure"""
        headers = {"X-API-Key": invalid_key}
        response = client.get("/test-mcp", headers=headers)

        assert response.status_code == 401

    def test_auth_dependency_factory(self, mock_env):
        """Test auth dependency factory function"""
        mcp_auth = get_auth_dependency(KeyType.MCP_OPERATIONS)

        # This would normally be tested in an async context
        # For now, just verify the function is created
        assert callable(mcp_auth)

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from wildeditor_auth.dependencies import (
    verify_api_key, 
    verify_mcp_key, 
    verify_backend_access_key,
    get_auth_dependency,
    RequireBackendKey,
    RequireMCPKey,
    RequireBackendAccessKey,
    auth_instance
)
from wildeditor_auth.api_key import KeyType


def create_test_app():
    """Create test app with fresh auth instance"""
    app = FastAPI()

    @app.get("/test-backend")
    async def test_backend_endpoint(authenticated: bool = RequireBackendKey):
        return {"message": "Backend access granted", "authenticated": authenticated}

    @app.get("/test-mcp")
    async def test_mcp_endpoint(authenticated: bool = RequireMCPKey):
        return {"message": "MCP access granted", "authenticated": authenticated}

    @app.get("/test-backend-access")
    async def test_backend_access_endpoint(authenticated: bool = RequireBackendAccessKey):
        return {"message": "Backend access granted", "authenticated": authenticated}
    
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
    
    def test_backend_auth_success(self, client, mock_env, valid_backend_key):
        """Test successful backend authentication"""
        headers = {"X-API-Key": valid_backend_key}
        response = client.get("/test-backend", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["authenticated"] is True
    
    def test_backend_auth_failure_invalid_key(self, client, mock_env, invalid_key):
        """Test backend authentication failure with invalid key"""
        headers = {"X-API-Key": invalid_key}
        response = client.get("/test-backend", headers=headers)
        
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]
    
    def test_backend_auth_failure_missing_key(self, client, mock_env):
        """Test backend authentication failure with missing key"""
        response = client.get("/test-backend")
        
        assert response.status_code == 401
        assert "Missing" in response.json()["detail"]
    
    def test_mcp_auth_success(self, client, mock_env, valid_mcp_key):
        """Test successful MCP authentication"""
        headers = {"X-API-Key": valid_mcp_key}
        response = client.get("/test-mcp", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["authenticated"] is True
    
    def test_mcp_auth_failure_wrong_key(self, client, mock_env, valid_backend_key):
        """Test MCP authentication failure with wrong key type"""
        headers = {"X-API-Key": valid_backend_key}
        response = client.get("/test-mcp", headers=headers)
        
        assert response.status_code == 401
    
    def test_backend_access_auth_success(self, client, mock_env, valid_mcp_backend_key):
        """Test successful backend access authentication"""
        headers = {"X-API-Key": valid_mcp_backend_key}
        response = client.get("/test-backend-access", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["authenticated"] is True
    
    def test_auth_dependency_factory(self, mock_env, valid_backend_key):
        """Test auth dependency factory function"""
        backend_auth = get_auth_dependency(KeyType.BACKEND_API)
        
        # This would normally be tested in an async context
        # For now, just verify the function is created
        assert callable(backend_auth)

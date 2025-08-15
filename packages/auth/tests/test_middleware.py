import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from wildeditor_auth.middleware import AuthMiddleware


# Create test FastAPI app with middleware
def create_test_app():
    app = FastAPI()
    
    # Add auth middleware
    app.add_middleware(
        AuthMiddleware,
        exclude_paths={"/health", "/docs"},
        mcp_path_prefix="/mcp",
        backend_path_prefix="/api"
    )
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    @app.get("/api/backend-endpoint")
    async def backend_endpoint():
        return {"message": "Backend endpoint"}
    
    @app.get("/mcp/mcp-endpoint")
    async def mcp_endpoint():
        return {"message": "MCP endpoint"}
    
    @app.get("/public")
    async def public_endpoint():
        return {"message": "Public endpoint"}
    
    return app


@pytest.fixture
def app():
    return create_test_app()


@pytest.fixture
def client(app):
    return TestClient(app)


class TestAuthMiddleware:
    """Test cases for AuthMiddleware"""
    
    def test_excluded_paths_no_auth(self, client):
        """Test that excluded paths don't require authentication"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_backend_endpoint_requires_auth(self, client, mock_env):
        """Test that backend endpoints require authentication"""
        # Without auth header
        response = client.get("/api/backend-endpoint")
        assert response.status_code == 401
        
        # With wrong key
        headers = {"X-API-Key": "wrong-key"}
        response = client.get("/api/backend-endpoint", headers=headers)
        assert response.status_code == 401
    
    def test_backend_endpoint_with_valid_auth(self, client, mock_env, valid_backend_key):
        """Test backend endpoint with valid authentication"""
        headers = {"X-API-Key": valid_backend_key}
        response = client.get("/api/backend-endpoint", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Backend endpoint"
    
    def test_mcp_endpoint_requires_auth(self, client, mock_env):
        """Test that MCP endpoints require authentication"""
        # Without auth header
        response = client.get("/mcp/mcp-endpoint")
        assert response.status_code == 401
        
        # With backend key (wrong type)
        headers = {"X-API-Key": "test-backend-key"}
        response = client.get("/mcp/mcp-endpoint", headers=headers)
        assert response.status_code == 401
    
    def test_mcp_endpoint_with_valid_auth(self, client, mock_env, valid_mcp_key):
        """Test MCP endpoint with valid authentication"""
        headers = {"X-API-Key": valid_mcp_key}
        response = client.get("/mcp/mcp-endpoint", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "MCP endpoint"
    
    def test_public_paths_no_auth_required(self, client):
        """Test that paths not matching prefixes don't require auth"""
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json()["message"] == "Public endpoint"
    
    def test_middleware_path_determination(self, mock_env):
        """Test path-based key type determination"""
        from wildeditor_auth.middleware import AuthMiddleware
        from wildeditor_auth.api_key import KeyType
        
        middleware = AuthMiddleware(
            None,  # app not needed for this test
            mcp_path_prefix="/mcp",
            backend_path_prefix="/api"
        )
        
        # Test path determination
        assert middleware._determine_key_type("/api/test") == KeyType.BACKEND_API
        assert middleware._determine_key_type("/mcp/test") == KeyType.MCP_OPERATIONS
        assert middleware._determine_key_type("/public") is None
        
        # Test exclusion
        assert middleware._should_exclude_path("/health") is True
        assert middleware._should_exclude_path("/docs") is True
        assert middleware._should_exclude_path("/api/test") is False

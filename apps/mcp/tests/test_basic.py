"""
Test basic MCP server functionality
"""

import pytest


class TestMCPServer:
    """Test MCP server basic functionality"""
    
    def test_health_check_public(self, client):
        """Test public health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "wildeditor-mcp-server"
        assert "version" in data
    
    def test_health_check_detailed_with_auth(self, client, mcp_headers):
        """Test detailed health check with authentication"""
        response = client.get("/health/detailed", headers=mcp_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["authenticated"] is True
        assert "features" in data
    
    def test_health_check_detailed_without_auth(self, client):
        """Test detailed health check fails without authentication"""
        response = client.get("/health/detailed")
        assert response.status_code == 401
    
    def test_mcp_status_with_auth(self, client, mcp_headers):
        """Test MCP status endpoint with authentication"""
        response = client.get("/mcp/status", headers=mcp_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "mcp_server" in data
        assert data["mcp_server"]["status"] == "ready"
        assert data["authenticated"] is True
    
    def test_mcp_status_without_auth(self, client):
        """Test MCP status endpoint fails without authentication"""
        response = client.get("/mcp/status")
        assert response.status_code == 401
    
    def test_mcp_initialize(self, client, mcp_headers):
        """Test MCP initialize endpoint"""
        response = client.post("/mcp/initialize", headers=mcp_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "result" in data
        assert "serverInfo" in data["result"]
        assert "capabilities" in data["result"]

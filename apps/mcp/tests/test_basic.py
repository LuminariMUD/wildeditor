"""
Test basic MCP server functionality
"""

import pytest
from unittest.mock import patch
import os


class TestMCPServer:
    """Test MCP server basic functionality"""
    
    @patch.dict(os.environ, {
        "WILDEDITOR_MCP_KEY": "test-mcp-key",
        "WILDEDITOR_API_KEY": "test-backend-key"
    })
    def test_health_check_public(self, client):
        """Test public health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "wildeditor-mcp-server"
        assert "version" in data
    
    @patch.dict(os.environ, {
        "WILDEDITOR_MCP_KEY": "test-mcp-key",
        "WILDEDITOR_API_KEY": "test-backend-key"
    })
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
    
    @patch.dict(os.environ, {
        "WILDEDITOR_MCP_KEY": "test-mcp-key",
        "WILDEDITOR_API_KEY": "test-backend-key"
    })
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
    
    @patch.dict(os.environ, {
        "WILDEDITOR_MCP_KEY": "test-mcp-key",
        "WILDEDITOR_API_KEY": "test-backend-key"
    })
    def test_mcp_initialize(self, client, mcp_headers):
        """Test MCP initialize endpoint"""
        response = client.post("/mcp/initialize", headers=mcp_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["initialized"] is True
        assert "server_info" in data
        assert "capabilities" in data

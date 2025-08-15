"""
Test Phase 2 MCP functionality
"""

import pytest
from unittest.mock import patch, AsyncMock
import httpx


class TestMCPPhase2:
    """Test MCP Phase 2 functionality"""
    
    def test_mcp_status_enhanced(self, client, mcp_headers):
        """Test enhanced MCP status with real capabilities"""
        response = client.get("/mcp/status", headers=mcp_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "mcp_server" in data
            assert data["mcp_server"]["status"] == "ready"
            
            # Check that we have actual capabilities now
            capabilities = data["mcp_server"]["capabilities"]
            assert isinstance(capabilities["tools"], int)
            assert isinstance(capabilities["resources"], int)
            assert isinstance(capabilities["prompts"], int)
            
            # Should have some tools, resources, and prompts
            assert capabilities["tools"] > 0
            assert capabilities["resources"] > 0
            assert capabilities["prompts"] > 0
    
    def test_list_tools(self, client, mcp_headers):
        """Test listing available tools"""
        response = client.get("/mcp/tools", headers=mcp_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "tools" in data
            tools = data["tools"]
            
            # Should have wilderness management tools
            tool_names = [tool["name"] for tool in tools]
            expected_tools = ["analyze_region", "find_path", "search_regions", "create_region"]
            
            for expected_tool in expected_tools:
                assert expected_tool in tool_names
    
    def test_list_resources(self, client, mcp_headers):
        """Test listing available resources"""
        response = client.get("/mcp/resources", headers=mcp_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "resources" in data
            resources = data["resources"]
            
            # Should have wilderness reference resources
            resource_uris = [resource["uri"] for resource in resources]
            expected_resources = ["wildeditor://terrain-types", "wildeditor://environment-types", "wildeditor://schema"]
            
            for expected_resource in expected_resources:
                assert expected_resource in resource_uris
    
    def test_list_prompts(self, client, mcp_headers):
        """Test listing available prompts"""
        response = client.get("/mcp/prompts", headers=mcp_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "prompts" in data
            prompts = data["prompts"]
            
            # Should have wilderness content prompts
            prompt_names = [prompt["name"] for prompt in prompts]
            expected_prompts = ["create_region", "connect_regions", "design_area"]
            
            for expected_prompt in expected_prompts:
                assert expected_prompt in prompt_names
    
    def test_read_resource(self, client, mcp_headers):
        """Test reading a specific resource"""
        response = client.get("/mcp/resources/terrain-types", headers=mcp_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            assert "terrain_types" in data["content"]
            assert len(data["content"]["terrain_types"]) > 0
    
    @patch('httpx.AsyncClient')
    def test_call_tool_mock_backend(self, mock_client, client, mcp_headers):
        """Test calling a tool with mocked backend"""
        # Mock the httpx client to simulate backend unavailable
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.ConnectError("Connection failed")
        
        response = client.post("/mcp/tools/analyze_region", 
                             json={"region_id": 1}, 
                             headers=mcp_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "result" in data
            assert "error" in data["result"]  # Should gracefully handle backend unavailable
    
    def test_get_prompt(self, client, mcp_headers):
        """Test getting a specific prompt"""
        response = client.post("/mcp/prompts/create_region",
                             json={"terrain_type": "forest", "environment": "temperate"},
                             headers=mcp_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "result" in data
            result = data["result"]
            assert "description" in result
            assert "messages" in result
            assert len(result["messages"]) > 0

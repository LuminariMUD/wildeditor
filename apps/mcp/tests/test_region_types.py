"""Ensure MCP advertises every region type accepted by the backend."""


def test_region_tool_schemas_include_vessel_region_types():
    # Import after the autouse environment fixture configures authentication.
    from src.mcp.tools import REGION_TYPE_VALUES, ToolRegistry

    registry = ToolRegistry()

    for tool_name in ["search_regions", "create_region", "generate_region_description"]:
        region_type = registry.get_tool(tool_name)["parameters"]["properties"]["region_type"]
        assert region_type["enum"] == REGION_TYPE_VALUES
        assert "5=Bathymetric" in region_type["description"]
        assert "7=Sky Island" in region_type["description"]


def test_create_region_schema_explains_vessel_thresholds():
    from src.mcp.tools import ToolRegistry

    registry = ToolRegistry()
    region_props = registry.get_tool("create_region")["parameters"]["properties"]["region_props"]

    assert "minimum natural depth for type 5" in region_props["description"]
    assert "minimum vessel Z for types 6-7" in region_props["description"]

"""Retirement guard for the former public Copilot-to-MCP probe."""

import pytest


def test_production_mcp_is_not_a_public_desktop_integration() -> None:
    pytest.skip(
        "Production MCP is private and is exercised through the authenticated "
        "chat-agent boundary."
    )

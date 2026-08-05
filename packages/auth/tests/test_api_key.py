import pytest
from wildeditor_auth.api_key import MultiKeyAuth, KeyType
from wildeditor_auth.exceptions import InvalidAPIKeyError, MissingAPIKeyError


class TestMultiKeyAuth:
    """Test cases for MultiKeyAuth class"""

    def test_init_with_environment_variables(self, mock_env):
        """Test initialization with environment variables"""
        auth = MultiKeyAuth()

        assert auth.has_valid_keys(KeyType.MCP_OPERATIONS)

        assert auth.get_key_count(KeyType.MCP_OPERATIONS) == 1

    def test_is_valid_key_with_correct_keys(
            self, mock_env, valid_mcp_key):
        """Test key validation with correct keys"""
        auth = MultiKeyAuth()

        assert auth.is_valid_key(valid_mcp_key, KeyType.MCP_OPERATIONS)

    def test_is_valid_key_with_invalid_keys(self, mock_env, invalid_key):
        """Test key validation with invalid keys"""
        auth = MultiKeyAuth()

        assert not auth.is_valid_key(invalid_key, KeyType.MCP_OPERATIONS)

    def test_is_valid_key_with_empty_key(self, mock_env):
        """Test key validation with empty key"""
        auth = MultiKeyAuth()

        assert not auth.is_valid_key("", KeyType.MCP_OPERATIONS)
        assert not auth.is_valid_key(None, KeyType.MCP_OPERATIONS)

    def test_verify_key_success(self, mock_env, valid_mcp_key):
        """Test successful key verification"""
        auth = MultiKeyAuth()

        result = auth.verify_key(valid_mcp_key, KeyType.MCP_OPERATIONS)
        assert result is True

    def test_verify_key_missing_key(self, mock_env):
        """Test verification with missing key"""
        auth = MultiKeyAuth()

        with pytest.raises(MissingAPIKeyError):
            auth.verify_key(None, KeyType.MCP_OPERATIONS)

        with pytest.raises(MissingAPIKeyError):
            auth.verify_key("", KeyType.MCP_OPERATIONS)

    def test_verify_key_invalid_key(self, mock_env, invalid_key):
        """Test verification with invalid key"""
        auth = MultiKeyAuth()

        with pytest.raises(InvalidAPIKeyError):
            auth.verify_key(invalid_key, KeyType.MCP_OPERATIONS)

    def test_add_key(self, mock_env):
        """Test adding new API keys"""
        auth = MultiKeyAuth()
        initial_count = auth.get_key_count(KeyType.MCP_OPERATIONS)

        auth.add_key("new-mcp-key", KeyType.MCP_OPERATIONS)
        assert auth.get_key_count(KeyType.MCP_OPERATIONS) == initial_count + 1
        assert auth.is_valid_key("new-mcp-key", KeyType.MCP_OPERATIONS)

    def test_remove_key(self, mock_env, valid_mcp_key):
        """Test removing API keys"""
        auth = MultiKeyAuth()

        assert auth.is_valid_key(valid_mcp_key, KeyType.MCP_OPERATIONS)
        auth.remove_key(valid_mcp_key, KeyType.MCP_OPERATIONS)
        assert not auth.is_valid_key(valid_mcp_key, KeyType.MCP_OPERATIONS)

    def test_add_empty_key_ignored(self, mock_env):
        """Test that empty keys are ignored when adding"""
        auth = MultiKeyAuth()
        initial_count = auth.get_key_count(KeyType.MCP_OPERATIONS)

        auth.add_key("", KeyType.MCP_OPERATIONS)
        auth.add_key(None, KeyType.MCP_OPERATIONS)

        assert auth.get_key_count(KeyType.MCP_OPERATIONS) == initial_count

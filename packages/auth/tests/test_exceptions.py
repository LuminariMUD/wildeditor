from wildeditor_auth.exceptions import (
    AuthenticationError,
    InvalidAPIKeyError,
    MissingAPIKeyError,
    UnauthorizedKeyTypeError
)


class TestExceptions:
    """Test cases for custom exceptions"""

    def test_authentication_error_default(self):
        """Test AuthenticationError with default message"""
        error = AuthenticationError()
        assert error.status_code == 401
        assert error.detail == "Authentication failed"

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message"""
        custom_message = "Custom auth failure"
        error = AuthenticationError(custom_message)
        assert error.status_code == 401
        assert error.detail == custom_message

    def test_invalid_api_key_error_default(self):
        """Test InvalidAPIKeyError with default key type"""
        error = InvalidAPIKeyError()
        assert error.status_code == 401
        assert "Invalid API key" in error.detail

    def test_invalid_api_key_error_custom_type(self):
        """Test InvalidAPIKeyError with custom key type"""
        key_type = "MCP"
        error = InvalidAPIKeyError(key_type)
        assert error.status_code == 401
        assert f"Invalid {key_type} key" in error.detail

    def test_missing_api_key_error(self):
        """Test MissingAPIKeyError"""
        error = MissingAPIKeyError()
        assert error.status_code == 401
        assert "Missing API key" in error.detail
        assert "X-API-Key header" in error.detail

    def test_unauthorized_key_type_error(self):
        """Test UnauthorizedKeyTypeError"""
        required_type = "backend_api"
        provided_type = "mcp_operations"
        error = UnauthorizedKeyTypeError(required_type, provided_type)

        assert error.status_code == 401
        assert required_type in error.detail
        assert provided_type in error.detail
        assert "Unauthorized" in error.detail

    def test_unauthorized_key_type_error_default_provided(self):
        """Test UnauthorizedKeyTypeError with default provided type"""
        required_type = "backend_api"
        error = UnauthorizedKeyTypeError(required_type)

        assert error.status_code == 401
        assert required_type in error.detail
        assert "unknown" in error.detail

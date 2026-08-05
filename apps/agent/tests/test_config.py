"""Chat runtime configuration safety tests."""

import pytest
from pydantic import ValidationError

from config import Settings
from session.storage import create_storage


def test_production_rejects_ephemeral_session_storage():
    with pytest.raises(ValidationError, match="STORAGE_BACKEND=redis"):
        Settings(
            _env_file=None,
            WILDEDITOR_ENVIRONMENT="remote-production",
            storage_backend="memory",
        )


def test_redis_storage_requires_a_connection_url():
    with pytest.raises(ValidationError, match="REDIS_URL is required"):
        Settings(
            _env_file=None,
            storage_backend="redis",
            redis_url="",
        )


def test_unknown_storage_backend_is_rejected():
    with pytest.raises(ValueError, match="Unsupported session storage backend"):
        create_storage("filesystem")

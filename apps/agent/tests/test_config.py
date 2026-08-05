"""Focused tests for chat-agent model configuration."""

import pytest
from pydantic import ValidationError

from src.config import Settings


@pytest.mark.parametrize(
    "model_name",
    ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"],
)
def test_supported_openai_models(model_name: str) -> None:
    settings = Settings(_env_file=None, model_name=model_name)

    assert settings.model_name == model_name


def test_legacy_openai_model_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, model_name="gpt-4.1")

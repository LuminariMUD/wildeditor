"""Focused tests for MCP OpenAI model selection."""

import pytest


@pytest.mark.parametrize(
    "model_name",
    ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"],
)
def test_supported_openai_models(monkeypatch: pytest.MonkeyPatch, model_name: str) -> None:
    from src.services.ai_service import get_openai_model_name

    monkeypatch.setenv("OPENAI_MODEL", model_name)

    assert get_openai_model_name() == model_name


def test_legacy_openai_model_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services.ai_service import get_openai_model_name

    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1")

    with pytest.raises(ValueError, match="supported GPT-5.6 model"):
        get_openai_model_name()

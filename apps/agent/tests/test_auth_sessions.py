"""Chat authentication, session ownership, and trusted MCP audit tests."""

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from wildeditor_auth import Principal, PrincipalKind, PrincipalRole

from agent.chat_agent import AssistantResponse
from routers import chat, health, session
from security import require_human_editor
from services.request_context import bind_request_context, reset_request_context
from services.mcp_client import MCPClient
from session.manager import SessionManager
from session.storage import InMemoryStorage


def human(subject: str, role: PrincipalRole = PrincipalRole.EDITOR):
    return Principal(
        kind=PrincipalKind.HUMAN,
        subject=subject,
        role=role,
        issuer="test-issuer",
    )


class DummyAgent:
    async def chat_with_history(self, *_args, **_kwargs):
        return AssistantResponse(message="ok")


def make_client():
    app = FastAPI()
    app.state.session_manager = SessionManager(InMemoryStorage(), ttl=3600)
    app.state.chat_agent = DummyAgent()
    app.include_router(session.router, prefix="/api/session")
    app.include_router(chat.router, prefix="/api/chat")
    current = {"principal": human("owner-a")}

    async def override_principal():
        return current["principal"]

    app.dependency_overrides[require_human_editor] = override_principal
    return TestClient(app), current


def test_create_session_uses_verified_subject_and_rejects_caller_user_id():
    client, _current = make_client()

    rejected = client.post("/api/session/", json={"user_id": "attacker"})
    assert rejected.status_code == 422

    created = client.post("/api/session/", json={"metadata": {"panel": "regions"}})
    assert created.status_code == 200
    session_id = created.json()["session_id"]

    info = client.get(f"/api/session/{session_id}")
    assert info.status_code == 200
    assert info.json()["user_id"] == "owner-a"


def test_other_user_cannot_read_mutate_or_stream_session():
    client, current = make_client()
    created = client.post("/api/session/", json={})
    session_id = created.json()["session_id"]
    current["principal"] = human("owner-b")

    responses = [
        client.get(f"/api/session/{session_id}"),
        client.put(f"/api/session/{session_id}/context", json={"context": {}}),
        client.post(f"/api/session/{session_id}/extend"),
        client.get(f"/api/chat/history?session_id={session_id}"),
        client.post(
            "/api/chat/message",
            json={"message": "hello", "session_id": session_id},
        ),
        client.post(
            "/api/chat/stream",
            json={"message": "hello", "session_id": session_id},
        ),
        client.delete(f"/api/chat/history/{session_id}"),
        client.delete(f"/api/session/{session_id}"),
    ]

    assert {response.status_code for response in responses} == {404}


def test_missing_token_is_rejected_by_real_chat_dependency():
    client, _current = make_client()
    client.app.dependency_overrides.clear()
    response = client.post("/api/session/", json={})
    assert response.status_code == 401


def test_malformed_token_is_401_not_configuration_503(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WILDEDITOR_AUTH_ISSUERS", "https://auth.example.test/auth/v1")
    client, _current = make_client()
    client.app.dependency_overrides.clear()
    response = client.post(
        "/api/session/",
        json={},
        headers={"Authorization": "Bearer malformed"},
    )
    assert response.status_code == 401


def test_request_context_contains_only_verified_actor_data():
    actor = human("verified-owner")
    token = bind_request_context(actor, "trusted-request-id")
    try:
        from services.request_context import current_request_context

        context = current_request_context.get()
        assert context is not None
        assert context.actor == "verified-owner"
        assert context.role == "editor"
        assert context.request_id == "trusted-request-id"
    finally:
        reset_request_context(token)


def test_mcp_client_authorizes_tool_and_propagates_audit_headers(monkeypatch):
    from config import settings

    captured = {}

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"result": {"content": [{"text": "{'ok': True}"}]}}

    class FakeHTTPClient:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, url, *, json, headers, timeout):
            captured.update({
                "url": url,
                "json": json,
                "headers": headers,
                "timeout": timeout,
            })
            return Response()

    monkeypatch.setattr(settings, "mcp_api_key", "test-mcp-key")
    monkeypatch.setattr("services.mcp_client.httpx.AsyncClient", FakeHTTPClient)
    client = MCPClient()
    context_token = bind_request_context(human("verified-owner"), "request-123")
    try:
        result = asyncio.run(client.call_tool("search_regions", {}))
    finally:
        reset_request_context(context_token)

    assert result == {"ok": True}
    assert captured["headers"]["X-API-Key"] == "test-mcp-key"
    assert captured["headers"]["X-Wildeditor-Actor"] == "verified-owner"
    assert captured["headers"]["X-Wildeditor-Request-ID"] == "request-123"


def test_mcp_client_denies_unknown_tools_before_network(monkeypatch):
    from config import settings

    monkeypatch.setattr(settings, "mcp_api_key", "test-mcp-key")
    client = MCPClient()
    context_token = bind_request_context(human("verified-owner"), "request-123")
    try:
        try:
            asyncio.run(client.call_tool("unreviewed_tool", {}))
        except PermissionError:
            pass
        else:
            raise AssertionError("unknown MCP tool was not denied")
    finally:
        reset_request_context(context_token)


class ReadyDependency:
    def __init__(self, ready: bool):
        self.ready = ready

    async def ping(self):
        return self.ready

    async def health_check(self):
        return self.ready


def make_health_client(storage_ready: bool, mcp_ready: bool):
    app = FastAPI()
    app.state.storage = ReadyDependency(storage_ready)
    app.state.mcp_client = ReadyDependency(mcp_ready)
    app.state.session_manager = object()
    app.state.chat_agent = object()
    app.include_router(health.router, prefix="/health")
    return TestClient(app)


def test_readiness_checks_storage_and_authenticated_mcp_chain():
    response = make_health_client(True, True).get("/health/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["checks"] == {
        "storage": True,
        "mcp": True,
        "session_manager": True,
        "chat_agent": True,
    }


@pytest.mark.parametrize(
    ("storage_ready", "mcp_ready"),
    [(False, True), (True, False)],
)
def test_readiness_returns_503_when_a_dependency_is_down(
    storage_ready,
    mcp_ready,
):
    response = make_health_client(storage_ready, mcp_ready).get("/health/ready")
    assert response.status_code == 503
    assert response.json()["ready"] is False

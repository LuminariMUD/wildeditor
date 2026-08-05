"""Server-only backend credential and actor-context propagation tests."""

import asyncio

from src.audit import AuditContext, _audit_context, backend_request_headers
from src.config import settings
from src.routers.health import backend_is_ready


def test_backend_headers_use_service_key_and_trusted_audit_context(monkeypatch):
    monkeypatch.setattr(settings, "backend_service_key", "server-only-key")
    token = _audit_context.set(AuditContext("user-123", "request-123"))
    try:
        headers = backend_request_headers()
    finally:
        _audit_context.reset(token)

    assert headers == {
        "Authorization": "Bearer server-only-key",
        "X-Wildeditor-Actor": "user-123",
        "X-Wildeditor-Request-ID": "request-123",
    }


def test_backend_readiness_proves_service_authentication(monkeypatch):
    captured = {}

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {
                "authenticated": True,
                "kind": "service",
                "role": "service",
            }

    class FakeHTTPClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, url, *, headers, timeout):
            captured.update({"url": url, "headers": headers, "timeout": timeout})
            return Response()

    monkeypatch.setattr(settings, "backend_service_key", "server-only-key")
    monkeypatch.setattr(settings, "backend_url", "http://backend.internal:8000")
    monkeypatch.setattr(
        "src.routers.health.httpx.AsyncClient",
        FakeHTTPClient,
    )

    assert asyncio.run(backend_is_ready()) is True
    assert captured == {
        "url": "http://backend.internal:8000/api/auth/status",
        "headers": {"Authorization": "Bearer server-only-key"},
        "timeout": 3.0,
    }

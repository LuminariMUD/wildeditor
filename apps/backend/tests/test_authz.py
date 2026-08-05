"""Authorization-boundary tests for every backend router class."""

import asyncio

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from wildeditor_auth import Principal, PrincipalKind, PrincipalRole

from src.middleware.auth import (
    is_auth_required,
    require_editor,
    require_human_editor,
    require_reader,
    verify_principal,
)
from src.routers.mcp_proxy import router as mcp_router
from src.routers.paths import router as paths_router
from src.routers.points import router as points_router
from src.routers.region_hints import router as region_hints_router
from src.routers.regions import router as regions_router
from src.routers.terrain import router as terrain_router
from src.routers.wilderness import router as wilderness_router


PROTECTED_ROUTERS = (
    ("/api/regions", regions_router),
    ("/api/regions", region_hints_router),
    ("/api/paths", paths_router),
    ("/api/points", points_router),
    ("/api/terrain", terrain_router),
    ("/api/wilderness", wilderness_router),
)


def principal(role: PrincipalRole, kind: PrincipalKind = PrincipalKind.HUMAN):
    return Principal(
        kind=kind,
        subject="subject-123",
        role=role,
        issuer="test-issuer",
    )


def dependency_calls(route: APIRoute) -> set[object]:
    calls: set[object] = set()

    def visit(dependant):
        for dependency in dependant.dependencies:
            call = dependency.call
            calls.add(call)
            visit(dependency)

    visit(route.dependant)
    return calls


def test_every_protected_router_has_the_expected_permission_dependency():
    inspected = 0
    for prefix, router in PROTECTED_ROUTERS:
        for route in router.routes:
            if not isinstance(route, APIRoute):
                continue
            full_path = f"{prefix}{route.path}"
            if full_path == "/api/terrain/health":
                continue

            inspected += 1
            calls = dependency_calls(route)
            assert require_reader in calls, full_path
            if route.methods & {"POST", "PUT", "PATCH", "DELETE"}:
                assert require_editor in calls, full_path

    assert inspected >= 30


def test_backend_mcp_proxy_is_human_editor_only():
    inspected = 0
    for route in mcp_router.routes:
        if not isinstance(route, APIRoute):
            continue
        inspected += 1
        assert require_human_editor in dependency_calls(route), route.path
    assert inspected == 3


@pytest.mark.parametrize(
    ("dependency", "caller"),
    [
        (require_editor, principal(PrincipalRole.VIEWER)),
        (require_human_editor, principal(PrincipalRole.VIEWER)),
        (
            require_human_editor,
            principal(PrincipalRole.SERVICE, PrincipalKind.SERVICE),
        ),
    ],
)
def test_valid_but_unauthorized_principals_receive_403(dependency, caller):
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(dependency(caller))
    assert exc_info.value.status_code == 403


@pytest.mark.parametrize(
    "caller",
    [
        principal(PrincipalRole.VIEWER),
        principal(PrincipalRole.EDITOR),
        principal(PrincipalRole.ADMIN),
        principal(PrincipalRole.SERVICE, PrincipalKind.SERVICE),
    ],
)
def test_read_authorization_matrix(caller):
    assert asyncio.run(require_reader(caller)) == caller


@pytest.mark.parametrize(
    "caller",
    [
        principal(PrincipalRole.EDITOR),
        principal(PrincipalRole.ADMIN),
        principal(PrincipalRole.SERVICE, PrincipalKind.SERVICE),
    ],
)
def test_editor_authorization_matrix(caller):
    assert asyncio.run(require_editor(caller)) == caller


def test_production_cannot_disable_authentication(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    monkeypatch.setenv("WILDEDITOR_ENVIRONMENT", "remote-production")

    assert is_auth_required() is True


def test_malformed_bearer_token_is_401_not_configuration_503(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("WILDEDITOR_AUTH_ISSUERS", "https://auth.example.test/auth/v1")
    app = FastAPI()

    @app.get("/protected")
    async def protected(_principal=Depends(verify_principal)):
        return {"ok": True}

    response = TestClient(app).get(
        "/protected",
        headers={"Authorization": "Bearer malformed"},
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

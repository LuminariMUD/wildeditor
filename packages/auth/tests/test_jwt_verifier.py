"""Focused tests for Supabase JWT verification and typed principals."""

import asyncio
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from wildeditor_auth import (
    BearerAuthenticator,
    JWTIssuer,
    JWTVerifier,
    PrincipalKind,
    PrincipalRole,
    TokenValidationError,
)


ISSUER = "https://auth.example.test/auth/v1"
AUDIENCE = "authenticated"


def make_key(key_id: str):
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = jwt.algorithms.ECAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    jwk.update({"kid": key_id, "alg": "ES256", "use": "sig"})
    return private_key, jwk


def make_token(
    private_key,
    key_id: str,
    *,
    role: str = "editor",
    issuer: str = ISSUER,
    audience: str = AUDIENCE,
    expires_delta: timedelta = timedelta(minutes=5),
    not_before: datetime | None = None,
    subject: str | None = "user-123",
    protected_top_level_role: bool = False,
    user_metadata_only: bool = False,
):
    now = datetime.now(UTC)
    claims = {
        "iss": issuer,
        "aud": audience,
        "exp": now + expires_delta,
        "iat": now,
        "email": "builder@example.test",
    }
    if subject is not None:
        claims["sub"] = subject
    if protected_top_level_role:
        claims["app_role"] = role
    elif user_metadata_only:
        claims["user_metadata"] = {"app_role": role}
    else:
        claims["app_metadata"] = {"app_role": role}
    if not_before:
        claims["nbf"] = not_before
    return jwt.encode(
        claims,
        private_key,
        algorithm="ES256",
        headers={"kid": key_id},
    )


class StaticFetcher:
    def __init__(self, *documents):
        self.documents = list(documents)
        self.calls = 0

    async def __call__(self, _url: str):
        index = min(self.calls, len(self.documents) - 1)
        self.calls += 1
        return self.documents[index]


def verifier(fetcher: StaticFetcher) -> JWTVerifier:
    return JWTVerifier(
        [JWTIssuer(ISSUER, f"{ISSUER}/.well-known/jwks.json", AUDIENCE)],
        allowed_algorithms=["ES256"],
        fetcher=fetcher,
    )


def run(coroutine):
    return asyncio.run(coroutine)


def test_rejects_oversized_token_without_fetching_jwks():
    fetcher = StaticFetcher({"keys": []})

    with pytest.raises(TokenValidationError, match="too large"):
        run(verifier(fetcher).verify("x" * 16_385))

    assert fetcher.calls == 0


@pytest.mark.parametrize("role", ["viewer", "editor", "admin"])
def test_valid_human_roles(role):
    private_key, jwk = make_key("primary")
    principal = run(
        verifier(StaticFetcher({"keys": [jwk]})).verify(
            make_token(private_key, "primary", role=role)
        )
    )

    assert principal.kind is PrincipalKind.HUMAN
    assert principal.role is PrincipalRole(role)
    assert principal.subject == "user-123"
    assert principal.issuer == ISSUER
    assert principal.email == "builder@example.test"


def test_accepts_protected_top_level_role_claim():
    private_key, jwk = make_key("primary")
    principal = run(
        verifier(StaticFetcher({"keys": [jwk]})).verify(
            make_token(
                private_key,
                "primary",
                role="admin",
                protected_top_level_role=True,
            )
        )
    )
    assert principal.role is PrincipalRole.ADMIN


@pytest.mark.parametrize(
    "token_factory",
    [
        lambda key: make_token(key, "primary", expires_delta=timedelta(seconds=-1)),
        lambda key: make_token(
            key,
            "primary",
            not_before=datetime.now(UTC) + timedelta(minutes=5),
        ),
        lambda key: make_token(key, "primary", issuer="https://attacker.test/auth/v1"),
        lambda key: make_token(key, "primary", audience="wrong-audience"),
        lambda key: make_token(key, "primary", subject=None),
        lambda key: make_token(key, "primary", user_metadata_only=True),
        lambda key: make_token(key, "primary", role="service"),
    ],
)
def test_rejects_invalid_claims(token_factory):
    private_key, jwk = make_key("primary")
    with pytest.raises(TokenValidationError):
        run(
            verifier(StaticFetcher({"keys": [jwk]})).verify(
                token_factory(private_key)
            )
        )


def test_rejects_wrong_signature_and_algorithm():
    private_key, jwk = make_key("primary")
    attacker_key, _ = make_key("attacker")
    auth = verifier(StaticFetcher({"keys": [jwk]}))

    with pytest.raises(TokenValidationError):
        run(auth.verify(make_token(attacker_key, "primary")))

    symmetric_token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "sub": "user-123",
            "app_metadata": {"app_role": "editor"},
        },
        "not-a-real-secret-with-at-least-32-bytes",
        algorithm="HS256",
        headers={"kid": "primary"},
    )
    with pytest.raises(TokenValidationError):
        run(auth.verify(symmetric_token))


def test_refreshes_jwks_once_when_a_new_key_id_appears():
    first_private, first_jwk = make_key("first")
    second_private, second_jwk = make_key("second")
    fetcher = StaticFetcher(
        {"keys": [first_jwk]},
        {"keys": [first_jwk, second_jwk]},
    )
    auth = verifier(fetcher)

    run(auth.verify(make_token(first_private, "first")))
    principal = run(auth.verify(make_token(second_private, "second")))

    assert principal.subject == "user-123"
    assert fetcher.calls == 2


def test_random_unknown_key_ids_cannot_force_unbounded_jwks_fetches():
    private_key, known_jwk = make_key("known")
    fetcher = StaticFetcher({"keys": [known_jwk]})
    auth = verifier(fetcher)

    for key_id in ("unknown-one", "unknown-two", "unknown-three"):
        with pytest.raises(TokenValidationError):
            run(auth.verify(make_token(private_key, key_id)))

    # Initial cache population plus one bounded unknown-kid refresh.
    assert fetcher.calls == 2


def test_service_key_is_separate_and_invalid_values_fall_through_to_jwt():
    private_key, jwk = make_key("primary")
    auth = BearerAuthenticator(
        verifier(StaticFetcher({"keys": [jwk]})),
        service_key="server-only-key",
        service_subject="mcp",
    )

    service = run(auth.authenticate("server-only-key"))
    assert service.kind is PrincipalKind.SERVICE
    assert service.role is PrincipalRole.SERVICE

    human = run(auth.authenticate(make_token(private_key, "primary")))
    assert human.kind is PrincipalKind.HUMAN

    with pytest.raises(TokenValidationError):
        run(auth.authenticate("wrong-key"))


def test_rejects_non_asymmetric_algorithm_configuration():
    with pytest.raises(ValueError):
        JWTVerifier(
            [JWTIssuer(ISSUER, f"{ISSUER}/.well-known/jwks.json")],
            allowed_algorithms=["HS256"],
        )

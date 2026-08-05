"""Asymmetric Supabase access-token verification with a bounded JWKS cache."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, Mapping, Optional

import httpx
import jwt

from .principal import Principal, PrincipalKind, PrincipalRole


class TokenValidationError(ValueError):
    """Raised when an access token cannot be trusted."""


@dataclass(frozen=True)
class JWTIssuer:
    """An explicitly trusted JWT issuer and its verification contract."""

    issuer: str
    jwks_url: str
    audience: str = "authenticated"

    def __post_init__(self) -> None:
        if not self.issuer or not self.jwks_url or not self.audience:
            raise ValueError("issuer, jwks_url, and audience must be non-empty")


@dataclass
class _CacheEntry:
    keys: dict[str, Mapping[str, Any]]
    expires_at: float


JWKSFetcher = Callable[[str], Awaitable[Mapping[str, Any]]]

ASYMMETRIC_ALGORITHMS = frozenset({
    "ES256",
    "ES384",
    "ES512",
    "EdDSA",
    "PS256",
    "PS384",
    "PS512",
    "RS256",
    "RS384",
    "RS512",
})


class JWTVerifier:
    """Verify JWTs only against an explicit issuer and algorithm allow-list."""

    def __init__(
        self,
        issuers: Iterable[JWTIssuer],
        *,
        allowed_algorithms: Iterable[str] = ("ES256",),
        cache_ttl_seconds: int = 300,
        fetcher: Optional[JWKSFetcher] = None,
    ) -> None:
        issuer_map = {item.issuer: item for item in issuers}
        if not issuer_map:
            raise ValueError("at least one trusted JWT issuer is required")

        algorithms = frozenset(allowed_algorithms)
        if not algorithms or not algorithms.issubset(ASYMMETRIC_ALGORITHMS):
            raise ValueError("only explicitly allowed asymmetric JWT algorithms may be used")

        self._issuers = issuer_map
        self._allowed_algorithms = algorithms
        self._cache_ttl_seconds = max(1, min(cache_ttl_seconds, 3600))
        self._fetcher = fetcher or self._fetch_jwks
        self._cache: dict[str, _CacheEntry] = {}
        self._last_forced_refresh: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def verify(self, token: str) -> Principal:
        """Return a human principal for a valid Supabase access token."""

        if not token:
            raise TokenValidationError("missing access token")
        if len(token) > 16_384:
            raise TokenValidationError("access token is too large")

        try:
            header = jwt.get_unverified_header(token)
            unverified = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
        except jwt.PyJWTError as exc:
            raise TokenValidationError("malformed access token") from exc

        algorithm = header.get("alg")
        key_id = header.get("kid")
        issuer_name = unverified.get("iss")
        if algorithm not in self._allowed_algorithms:
            raise TokenValidationError("access token uses a disallowed algorithm")
        if not isinstance(key_id, str) or not key_id or len(key_id) > 200:
            raise TokenValidationError("access token is missing a key identifier")
        if not isinstance(issuer_name, str) or issuer_name not in self._issuers:
            raise TokenValidationError("access token issuer is not trusted")

        issuer = self._issuers[issuer_name]
        jwk = await self._get_key(issuer, key_id)
        try:
            signing_key = jwt.PyJWK.from_dict(dict(jwk), algorithm=algorithm).key
            claims = jwt.decode(
                token,
                key=signing_key,
                algorithms=[algorithm],
                audience=issuer.audience,
                issuer=issuer.issuer,
                options={"require": ["iss", "aud", "exp", "sub"]},
            )
        except (jwt.PyJWTError, ValueError, TypeError) as exc:
            raise TokenValidationError("invalid access token") from exc

        subject = claims.get("sub")
        if (
            not isinstance(subject, str)
            or not subject.strip()
            or len(subject) > 200
            or any(ord(character) < 32 for character in subject)
        ):
            raise TokenValidationError("access token subject is invalid")

        role = self._extract_role(claims)
        email = claims.get("email")
        if not (
            isinstance(email, str)
            and len(email) <= 320
            and not any(ord(character) < 32 for character in email)
        ):
            email = None
        return Principal(
            kind=PrincipalKind.HUMAN,
            subject=subject,
            role=role,
            issuer=issuer.issuer,
            email=email,
        )

    async def _get_key(
        self,
        issuer: JWTIssuer,
        key_id: str,
    ) -> Mapping[str, Any]:
        keys = await self._get_cached_keys(issuer)
        key = keys.get(key_id)
        if key is not None:
            return key

        # A signing-key rotation can introduce a new kid before the cache expires.
        keys = await self._get_cached_keys(issuer, force_refresh=True)
        key = keys.get(key_id)
        if key is None:
            raise TokenValidationError("access token signing key is unknown")
        return key

    async def _get_cached_keys(
        self,
        issuer: JWTIssuer,
        *,
        force_refresh: bool = False,
    ) -> dict[str, Mapping[str, Any]]:
        now = time.monotonic()
        entry = self._cache.get(issuer.issuer)
        if not force_refresh and entry and entry.expires_at > now:
            return entry.keys

        async with self._lock:
            now = time.monotonic()
            entry = self._cache.get(issuer.issuer)
            if not force_refresh and entry and entry.expires_at > now:
                return entry.keys
            if (
                force_refresh
                and entry
                and self._last_forced_refresh.get(issuer.issuer, 0) > now - 5
            ):
                # A random-kid token must not turn JWKS refresh into an
                # attacker-controlled outbound request on every API call.
                return entry.keys

            document = await self._fetcher(issuer.jwks_url)
            raw_keys = document.get("keys")
            if not isinstance(raw_keys, list):
                raise TokenValidationError("JWKS response does not contain a key list")

            keys: dict[str, Mapping[str, Any]] = {}
            for raw_key in raw_keys:
                if not isinstance(raw_key, Mapping):
                    continue
                key_id = raw_key.get("kid")
                if isinstance(key_id, str) and key_id:
                    keys[key_id] = raw_key

            if not keys:
                raise TokenValidationError("JWKS response contains no usable keys")

            self._cache[issuer.issuer] = _CacheEntry(
                keys=keys,
                expires_at=now + self._cache_ttl_seconds,
            )
            if force_refresh:
                self._last_forced_refresh[issuer.issuer] = now
            return keys

    @staticmethod
    async def _fetch_jwks(url: str) -> Mapping[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
                response = await client.get(url, headers={"Accept": "application/json"})
                response.raise_for_status()
                if len(response.content) > 1_048_576:
                    raise TokenValidationError("JWKS response is too large")
                document = response.json()
        except TokenValidationError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            raise TokenValidationError("unable to refresh signing keys") from exc

        if not isinstance(document, Mapping):
            raise TokenValidationError("JWKS response is not an object")
        return document

    @staticmethod
    def _extract_role(claims: Mapping[str, Any]) -> PrincipalRole:
        # app_metadata is set by Auth administration and cannot be changed by a
        # user. A custom access-token hook may alternatively expose app_role as
        # a protected top-level claim. user_metadata is intentionally ignored.
        raw_role = claims.get("app_role")
        if raw_role is None:
            app_metadata = claims.get("app_metadata")
            if isinstance(app_metadata, Mapping):
                raw_role = app_metadata.get("app_role")

        try:
            role = PrincipalRole(raw_role)
        except (TypeError, ValueError) as exc:
            raise TokenValidationError("access token has no valid protected role") from exc

        if role is PrincipalRole.SERVICE:
            raise TokenValidationError("human access token cannot use the service role")
        return role

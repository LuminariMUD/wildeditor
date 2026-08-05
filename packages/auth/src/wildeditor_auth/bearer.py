"""Bearer-token authentication for human JWTs and server-only credentials."""

from __future__ import annotations

import hmac
from typing import Optional

from .jwt_verifier import JWTVerifier, TokenValidationError
from .principal import Principal, PrincipalKind, PrincipalRole


class BearerAuthenticator:
    """Authenticate a human JWT or an optional server-to-server credential."""

    def __init__(
        self,
        jwt_verifier: JWTVerifier,
        *,
        service_key: Optional[str] = None,
        service_subject: str = "mcp",
    ) -> None:
        self.jwt_verifier = jwt_verifier
        self.service_key = service_key or None
        self.service_subject = service_subject

    async def authenticate(
        self,
        credential: str,
        *,
        allow_service: bool = True,
    ) -> Principal:
        if (
            allow_service
            and self.service_key
            and hmac.compare_digest(credential, self.service_key)
        ):
            return Principal(
                kind=PrincipalKind.SERVICE,
                subject=self.service_subject,
                role=PrincipalRole.SERVICE,
                issuer="wildeditor-service-key",
            )

        try:
            return await self.jwt_verifier.verify(credential)
        except TokenValidationError:
            # Do not reveal whether a credential resembled a service key, JWT,
            # known issuer, or signing key.
            raise

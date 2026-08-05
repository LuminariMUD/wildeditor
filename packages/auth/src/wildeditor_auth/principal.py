"""Typed authenticated principals and Wildeditor authorization roles."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PrincipalKind(str, Enum):
    """The trust mechanism that produced a principal."""

    HUMAN = "human"
    SERVICE = "service"
    DEVELOPMENT = "development"


class PrincipalRole(str, Enum):
    """Protected Wildeditor authorization roles."""

    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    SERVICE = "service"


class Principal(BaseModel):
    """A verified caller. Tokens and credentials are never retained here."""

    model_config = ConfigDict(frozen=True)

    kind: PrincipalKind
    subject: str
    role: PrincipalRole
    issuer: str
    email: Optional[str] = None

    @property
    def is_human(self) -> bool:
        return self.kind in {PrincipalKind.HUMAN, PrincipalKind.DEVELOPMENT}


DEVELOPMENT_PRINCIPAL = Principal(
    kind=PrincipalKind.DEVELOPMENT,
    subject="local-development",
    role=PrincipalRole.ADMIN,
    issuer="local-development",
)

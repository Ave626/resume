from dataclasses import dataclass
from app.features.auth.domain.entities.user import UserRole
from uuid import UUID

@dataclass(slots=True)
class TokenPayload:
    sub : UUID
    exp : int
    role: UserRole | None = None
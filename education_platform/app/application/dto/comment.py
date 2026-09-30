from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.comment import CommentTargetType


@dataclass(slots=True)
class CommentDTO:
    id: UUID
    target_type: CommentTargetType
    target_id: UUID
    user_id: UUID
    text: str
    created_at: datetime
    updated_at: datetime | None

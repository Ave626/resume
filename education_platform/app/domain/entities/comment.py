from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidCommentError


class CommentTargetType(StrEnum):
    LECTURE = "lecture"
    QUESTION = "question"
    TASK = "task"
    CODE_TASK = "code_task"


@dataclass(frozen=True, slots=True)
class CommentTarget:
    type: CommentTargetType
    id: UUID


@dataclass(slots=True)
class Comment:
    id: UUID
    target: CommentTarget
    user_id: UUID
    text: str
    created_at: datetime
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate_text(self.text)
        self.text = self.text.strip()

    def update_text(self, new_text: str) -> None:
        self._validate_text(new_text)
        self.text = new_text.strip()
        self.updated_at = datetime.now(UTC)

    @staticmethod
    def _validate_text(text: str) -> None:
        cleaned = text.strip() if text else ""
        if not cleaned:
            raise InvalidCommentError("Comment text cannot be empty.")
        if len(cleaned) > 2000:
            raise InvalidCommentError("Comment text cannot exceed 2000 characters.")

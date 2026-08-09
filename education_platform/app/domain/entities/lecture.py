from dataclasses import dataclass
from uuid import UUID

from app.domain.exceptions import InvalidLectureError


@dataclass(slots=True)
class Lecture:
    id: UUID
    section_id: UUID
    title: str
    content: str
    position: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidLectureError("Название лекции не может быть пустым")
        if not self.content or not self.content.strip():
            raise InvalidLectureError("Контент лекции не может быть пустым")
        if self.position < 1:
            raise InvalidLectureError("Позиция должна быть строго положительна")

    def update(self, title: str, content: str, position: str) -> None:
        self.title = title
        self.content = content
        self.position = position
        self._validate()

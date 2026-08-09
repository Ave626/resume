from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.question import Question


class QuestionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, question_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, question_id: list[UUID]) -> list[Question]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, question: Question) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, question: Question) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, question_id: UUID) -> None:
        raise NotImplementedError

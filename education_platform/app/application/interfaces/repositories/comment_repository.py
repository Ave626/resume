from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.comment import Comment, CommentTarget


class CommentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_target(self, target: CommentTarget) -> list[Comment]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, comment: Comment) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, comment: Comment) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, comment_id: UUID) -> None:
        raise NotImplementedError

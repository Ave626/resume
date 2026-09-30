from dataclasses import dataclass
from uuid import UUID

from app.application.dto.comment import CommentDTO
from app.application.exceptions import CommentNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateCommentCommand:
    comment_id: UUID
    text: str
    actor: User


class UpdateCommentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: UpdateCommentCommand) -> CommentDTO:
        async with self.uow:
            comment = await self.uow.comments.get_by_id(command.comment_id)
            if comment is None:
                raise CommentNotFoundError("Comment not found.")

            if comment.user_id != command.actor.id:
                raise PermissionDeniedError("Cannot edit another user's comment.")

            comment.update_text(command.text)
            await self.uow.comments.update(comment)
            await self.uow.commit()

            return CommentDTO(
                id=comment.id,
                target_type=comment.target.type,
                target_id=comment.target.id,
                user_id=comment.user_id,
                text=comment.text,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )

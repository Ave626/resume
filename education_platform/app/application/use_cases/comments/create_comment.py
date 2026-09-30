from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.comment import CommentDTO
from app.application.exceptions import PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.comment_target_resolver import CommentTargetResolver
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.comment import Comment, CommentTarget
from app.domain.entities.user import User


@dataclass(slots=True)
class CreateCommentCommand:
    target: CommentTarget
    text: str
    actor: User


class CreateCommentUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        target_resolver: CommentTargetResolver,
        access_service: CourseContentAccessService,
    ) -> None:
        self.uow = uow
        self.target_resolver = target_resolver
        self.access_service = access_service

    async def execute(self, command: CreateCommentCommand) -> CommentDTO:
        if not command.actor.is_student():
            raise PermissionDeniedError("Only students can leave comments.")

        async with self.uow:
            section_id = await self.target_resolver.resolve_section_id(
                self.uow,
                command.target,
            )
            can_view = await self.access_service.can_view_section_content(
                section_id=section_id,
                actor=command.actor,
            )
            if not can_view:
                raise PermissionDeniedError("Cannot comment on inaccessible target.")

            comment = Comment(
                id=uuid4(),
                target=command.target,
                user_id=command.actor.id,
                text=command.text,
                created_at=datetime.now(UTC),
            )
            await self.uow.comments.add(comment)
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

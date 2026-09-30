from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CommentNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.comment_target_resolver import CommentTargetResolver
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteCommentCommand:
    comment_id: UUID
    actor: User


class DeleteCommentUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        target_resolver: CommentTargetResolver,
        access_service: CourseContentAccessService,
    ) -> None:
        self.uow = uow
        self.target_resolver = target_resolver
        self.access_service = access_service

    async def execute(self, command: DeleteCommentCommand) -> None:
        async with self.uow:
            comment = await self.uow.comments.get_by_id(command.comment_id)
            if comment is None:
                raise CommentNotFoundError("Comment not found.")

            is_owner = comment.user_id == command.actor.id
            is_admin = command.actor.can_manage_platform()

            if not (is_owner or is_admin):
                section_id = await self.target_resolver.resolve_section_id(
                    self.uow,
                    comment.target,
                )
                course = await self.access_service.get_course_by_section_id(section_id)
                if course is None or not course.is_owned_by(command.actor.id):
                    raise PermissionDeniedError("Permission denied.")

            await self.uow.comments.delete(comment.id)
            await self.uow.commit()

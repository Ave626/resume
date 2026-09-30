from dataclasses import dataclass

from app.application.dto.comment import CommentDTO
from app.application.exceptions import LectureNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.comment_target_resolver import CommentTargetResolver
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.comment import CommentTarget
from app.domain.entities.user import User


@dataclass(slots=True)
class GetCommentsByTargetQuery:
    target: CommentTarget
    actor: User | None = None


class GetCommentsByTargetUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        target_resolver: CommentTargetResolver,
        access_service: CourseContentAccessService,
    ) -> None:
        self.uow = uow
        self.target_resolver = target_resolver
        self.access_service = access_service

    async def execute(self, query: GetCommentsByTargetQuery) -> list[CommentDTO]:
        async with self.uow:
            section_id = await self.target_resolver.resolve_section_id(
                self.uow,
                query.target,
            )
            can_view = await self.access_service.can_view_section_content(
                section_id=section_id,
                actor=query.actor,
            )
            if not can_view:
                raise LectureNotFoundError("Target content not found.")

            comments = await self.uow.comments.list_by_target(query.target)
            return [
                CommentDTO(
                    id=c.id,
                    target_type=c.target.type,
                    target_id=c.target.id,
                    user_id=c.user_id,
                    text=c.text,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                )
                for c in comments
            ]

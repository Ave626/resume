from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.comment_repository import CommentRepository
from app.domain.entities.comment import Comment, CommentTarget, CommentTargetType
from app.infrastructure.database.mappers.comment_mapper import CommentMapper
from app.infrastructure.database.models.comment_model import CommentModel


class SqlAlchemyCommentRepository(CommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        model = await self.session.get(CommentModel, str(comment_id))
        return None if model is None else CommentMapper.to_domain(model)

    async def list_by_target(self, target: CommentTarget) -> list[Comment]:
        column_map = {
            CommentTargetType.LECTURE: CommentModel.lecture_id,
            CommentTargetType.QUESTION: CommentModel.question_id,
            CommentTargetType.TASK: CommentModel.task_id,
            CommentTargetType.CODE_TASK: CommentModel.code_task_id,
        }

        column = column_map.get(target.type)

        stmt = (
            select(CommentModel)
            .where(column == str(target.id))
            .order_by(CommentModel.created_at.asc(), CommentModel.id.asc())
        )
        result = await self.session.execute(stmt)
        return [CommentMapper.to_domain(model) for model in result.scalars().all()]

    async def add(self, comment: Comment) -> None:
        self.session.add(CommentMapper.to_model(comment))
        await self.session.flush()

    async def update(self, comment: Comment) -> None:
        model = await self.session.get(CommentModel, str(comment.id))
        if model is None:
            return
        model.text = comment.text
        model.updated_at = comment.updated_at
        await self.session.flush()

    async def delete(self, comment_id: UUID) -> None:
        model = await self.session.get(CommentModel, str(comment_id))
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()

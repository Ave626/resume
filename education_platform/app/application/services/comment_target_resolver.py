from collections.abc import Awaitable, Callable
from uuid import UUID

from app.application.exceptions import (
    CodeTaskNotFoundError,
    LectureNotFoundError,
    QuestionNotFoundError,
    TaskNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.comment import CommentTarget, CommentTargetType

TargetResolver = Callable[[UnitOfWork, UUID], Awaitable[UUID]]


class CommentTargetResolver:
    def __init__(self) -> None:
        self._resolvers: dict[CommentTargetType, TargetResolver] = {
            CommentTargetType.LECTURE: self._resolve_lecture,
            CommentTargetType.TASK: self._resolve_task,
            CommentTargetType.CODE_TASK: self._resolve_code_task,
            CommentTargetType.QUESTION: self._resolve_question,
        }

    async def resolve_section_id(
        self,
        uow: UnitOfWork,
        target: CommentTarget,
    ) -> UUID:
        resolver = self._resolvers.get(target.type)
        if resolver is None:
            raise ValueError(f"Unsupported comment target type: {target.type}")
        return await resolver(uow, target.id)

    @staticmethod
    async def _resolve_lecture(uow: UnitOfWork, target_id: UUID) -> UUID:
        lecture = await uow.lectures.get_by_id(target_id)
        if lecture is None:
            raise LectureNotFoundError("Lecture not found.")
        return lecture.section_id

    @staticmethod
    async def _resolve_task(uow: UnitOfWork, target_id: UUID) -> UUID:
        task = await uow.tasks.get_by_id(target_id)
        if task is None:
            raise TaskNotFoundError("Task not found.")
        return task.section_id

    @staticmethod
    async def _resolve_code_task(uow: UnitOfWork, target_id: UUID) -> UUID:
        code_task = await uow.code_tasks.get_by_id(target_id)
        if code_task is None:
            raise CodeTaskNotFoundError("Code task not found.")
        return code_task.section_id

    @staticmethod
    async def _resolve_question(uow: UnitOfWork, target_id: UUID) -> UUID:
        question = await uow.questions.get_by_id(target_id)
        if question is None:
            raise QuestionNotFoundError("Question not found.")
        return question.section_id

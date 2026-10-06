from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    QuestionAlreadyUsedError,
    QuestionNotFoundError,
)
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities import Question, QuestionType, User


@dataclass(slots=True)
class UpdateQuestionCommand:
    actor: User
    question_id: UUID
    text: str
    position: int
    question_type: QuestionType
    max_attempts: int
    reward_points: int


class UpdateQuestionUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ):
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateQuestionCommand) -> Question:

        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError("Question not found")

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=question.section_id,
            )
            section = await self.uow.sections.get_by_id(question.section_id)
            module = await self.uow.modules.get_by_id(section.module_id) if section is not None else None

            has_attempts = await self.uow.question_attempts.exists_by_question_id(
                question.id
            )
            if has_attempts:
                raise QuestionAlreadyUsedError(
                    "Question alredy has student attempt and cannot be changed"
                )

            question.update(
                text=command.text,
                position=command.position,
                question_type=command.question_type,
                max_attempts=command.max_attempts,
                reward_points=command.reward_points,
            )
            await self.uow.questions.update(question)
            await self.uow.commit()
            if self.content_cache is not None and module is not None:
                await self.content_cache.invalidate_course(module.course_id)
            return question

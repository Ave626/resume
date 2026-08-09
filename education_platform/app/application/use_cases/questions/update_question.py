from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    PermissionDeniedError,
    QuestionAlreadyUsedError,
    QuestionNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities import Question, QuestionType, User
from app.application.interfaces.services.course_access_service import CourseAccessService


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
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateQuestionCommand) -> Question:

        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError("Question not found")

            await self.course_access_service.ensure_can_manage_section(  #
                actor=command.actor,
                section_id=question.section_id,
            )

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
            return question

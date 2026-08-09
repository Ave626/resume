from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    AnswerOptionNotFoundError,
    PermissionDeniedError,
    QuestionAlreadyUsedError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities import User
from app.application.interfaces.services.course_access_service


@dataclass(slots=True)
class UpdateAnswerOptionCommand:
    actor: User
    answer_option_id: UUID
    text: str
    position: int
    is_correct: bool


class UpdateAnswerOptionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: UpdateAnswerOptionCommand) -> None:

        async with self.uow:
            answer_option = await self.uow.answer_options.get_by_id(
                command.answer_option_id
            )
            if answer_option is None:
                raise AnswerOptionNotFoundError("Answer option not found")

            qusetion = aw

            has_attempts = await self.uow.question_attempts.exists_by_question_id(
                answer_option.question_id
            )
            if has_attempts:
                raise QuestionAlreadyUsedError(
                    "Question already has student attempts and cannot be changed safely."
                )

            answer_option.update(
                text=command.text,
                position=command.position,
                is_correct=command.is_correct,
            )
            await self.uow.answer_options.update(answer_option)
            await self.uow.commit()
            return answer_option

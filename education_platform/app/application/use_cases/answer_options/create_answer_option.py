from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import QuestionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities import AnswerOption, User
from app.application.services.course_access_service import CourseAccessService

@dataclass(slots=True)
class CreateAnswerOptionCommand:
    actor: User
    question_id: UUID
    text: str
    position: int
    is_correct: bool = False


class CreateAnswerOptionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateAnswerOptionCommand) -> None:
        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError("Question not found.")
            await self.course_access_service.ensure_can_manage_section(command.actor,question.section_id)
            answer_option = AnswerOption(
                id=uuid4(),
                question_id=command.question_id,
                text=command.text,
                position=command.position,
                is_correct=command.is_correct,
            )
            question.add_answer_option(answer_option.id)
            await self.uow.answer_options.add(answer_option)
            await self.uow.questions.update(question)
            await self.uow.commit()
            return answer_option

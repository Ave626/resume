from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import QuestionNotFoundError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities import AnswerOption, User


@dataclass(slots=True)
class CreateAnswerOptionCommand:
    actor: User
    question_id: UUID
    text: str
    position: int
    is_correct: bool = False


class CreateAnswerOptionUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ):
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateAnswerOptionCommand) -> None:
        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError("Question not found.")
            await self.course_access_service.ensure_can_manage_section(
                command.actor, question.section_id
            )
            section = await self.uow.sections.get_by_id(question.section_id)
            module = await self.uow.modules.get_by_id(section.module_id) if section is not None else None

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
            if self.content_cache is not None and module is not None:
                await self.content_cache.invalidate_course(module.course_id)
            return answer_option

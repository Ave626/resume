from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    CodeTaskAlreadyUsedError,
    CodeTaskNotFoundError,
    TestCaseNotFoundError,
)
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.test_case import TestCase
from app.domain.entities.user import User
from app.domain.exceptions import InvalidCodeTaskError


@dataclass(slots=True)
class UpdateTestCaseCommand:
    actor: User
    test_case_id: UUID
    position: int
    input_data: str
    expected_output: str
    is_hidden: bool
    explanation: str = ""


class UpdateTestCaseUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateTestCaseCommand) -> TestCase:
        async with self.uow:
            test_case = await self.uow.test_cases.get_by_id(command.test_case_id)
            if test_case is None:
                raise TestCaseNotFoundError("TestCase not found")

            code_task = await self.uow.code_tasks.get_by_id(test_case.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError("CodeTask not found")

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=code_task.section_id,
            )
            section = await self.uow.sections.get_by_id(code_task.section_id)
            module = await self.uow.modules.get_by_id(section.module_id) if section is not None else None

            has_submissions = await self.uow.code_submissions.exists_by_code_task_id(
                code_task.id
            )

            try:
                code_task.ensure_test_cases_can_be_changed(has_submissions)
            except InvalidCodeTaskError as exc:
                raise CodeTaskAlreadyUsedError(str(exc)) from exc

            test_case.update(
                input_data=command.input_data,
                expected_output=command.expected_output,
                is_hidden=command.is_hidden,
                explanation=command.explanation,
                position=command.position,
            )

            await self.uow.test_cases.update(test_case)
            await self.uow.commit()
            if self.content_cache is not None and module is not None:
                await self.content_cache.invalidate_course(module.course_id)
            return test_case

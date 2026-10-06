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


@dataclass
class DeleteTestCaseCommand:
    test_case_id: UUID
    actor: User


class DeleteTestCaseUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteTestCaseCommand) -> None:
        async with self.uow:
            test_case = await self.uow.test_cases.get_by_id(command.test_case_id)
            if test_case is None:
                raise TestCaseNotFoundError("TestCase not found")

            code_task = await self.uow.code_tasks.get_by_id(test_case.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError("Code_Task not found")

            test_cases = await self.uow.test_cases.list_by_code_task_id(code_task.id)
            code_task.test_case_ids = [item.id for item in test_cases]

            has_submissions = await self.uow.code_submissions.exists_by_code_task_id(
                code_task.id
            )
            if has_submissions:
                raise CodeTaskAlreadyUsedError(
                    "Cannot delete test case: code task already has student submissions"
                )

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor, section_id=code_task.section_id
            )
            section = await self.uow.sections.get_by_id(code_task.section_id)
            module = await self.uow.modules.get_by_id(section.module_id) if section is not None else None

            code_task.remove_test_case(test_case.id)
            code_task.ensure_has_test_cases()
            await self.uow.code_tasks.update(code_task)
            await self.uow.test_cases.delete(test_case)
            await self.uow.commit()
            if self.content_cache is not None and module is not None:
                await self.content_cache.invalidate_course(module.course_id)

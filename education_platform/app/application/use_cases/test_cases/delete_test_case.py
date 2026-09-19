from dataclasses import dataclass
from uuid import UUID
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User
from app.domain.entities.test_case import TestCase
from app.application.exceptions import (
    CodeTaskAlreadyUsedError,
    CodeTaskNotFoundError,
    TestCaseNotFoundError,
)

from app.application.services.course_access_service import CourseAccessService

@dataclass
class DeleteTestCaseCommand:
    test_case_id : UUID
    actor : User

class DeleteTestCaseUseCase:
    def __init__(self,uow : UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
    
    async def execute(self,command : DeleteTestCaseCommand) -> None:
        async with self.uow:
            test_case = await self.uow.test_cases.get_by_id(command.test_case_id)
            if test_case is None:
                raise TestCaseNotFoundError("TestCase not found")
            
            code_task = await self.uow.code_tasks.get_by_id(test_case.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError("Code_Task not found")
            
            has_submissions = await self.uow.code_submissions.exists_by_code_task_id(code_task.id)
            if has_submissions:
                raise CodeTaskAlreadyUsedError(
                    "Cannot delete test case: code task already has student submissions"
                )
            
            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=code_task.section_id
            )

            code_task.remove_test_case(test_case.id)
            await self.uow.code_tasks.update(code_task)
            await self.uow.test_cases.delete(test_case)
            await self.uow.commit()
        
from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import ModuleNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User
from app.application.interfaces.services.course_access_service import CourseAccessService

@dataclass(slots=True)
class DeleteModuleCommand:
    module_id: UUID
    actor : User


class DeleteModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteModuleCommand) -> None:
        async with self.uow:
            module = await self.uow.modules.get_by_id(command.module_id)
            if module is None:
                raise ModuleNotFoundError("Module not found")
            await self.course_access_service.ensure_can_manage_module(module_id=module.id,actor=command.actor)
            course = await self.uow.courses.get_by_id(module.course_id)
            if course is not None:
                course.remove_module(module.id)
                await self.uow.courses.update(course)
            await self.uow.modules.delete(module)
            await self.uow.commit()

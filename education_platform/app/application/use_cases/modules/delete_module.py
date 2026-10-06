from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import ModuleNotFoundError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteModuleCommand:
    module_id: UUID
    actor: User


class DeleteModuleUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteModuleCommand) -> None:
        async with self.uow:
            module = await self.uow.modules.get_by_id(command.module_id)
            if module is None:
                raise ModuleNotFoundError("Module not found")
            await self.course_access_service.ensure_can_manage_module(
                module_id=module.id, actor=command.actor
            )
            course_id = module.course_id
            course = await self.uow.courses.get_by_id(course_id)
            if course is not None:
                course.remove_module(module.id)
                await self.uow.courses.update(course)
            await self.uow.modules.delete(module)
            await self.uow.commit()
            if self.content_cache is not None:
                await self.content_cache.invalidate_course(course_id)

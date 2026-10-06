from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import ModuleNotFoundError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.module import Module
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateModuleCommand:
    module_id: UUID
    title: str
    description: str
    position: int
    actor: User


class UpdateModuleUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateModuleCommand) -> Module:
        async with self.uow:
            module = await self.uow.modules.get_by_id(command.module_id)
            if module is None:
                raise ModuleNotFoundError("Такого модуля нет")
            await self.course_access_service.ensure_can_manage_module(
                command.actor, module.id
            )
            module.update(
                title=command.title,
                description=command.description,
                position=command.position,
            )
            await self.uow.modules.update(module)
            await self.uow.commit()
            if self.content_cache is not None:
                await self.content_cache.invalidate_course(module.course_id)
            return module

from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import SectionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User
from app.application.interfaces.services.course_access_service import CourseAccessService

@dataclass(slots=True)
class DeleteSectionCommand:
    section_id: UUID
    actor : User


class DeleteSectionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteSectionCommand) -> None:
        async with self.uow:
            section = await self.uow.sections.get_by_id(command.section_id)
            if section is None:
                raise SectionNotFoundError("Section not found")
            await self.course_access_service.ensure_can_manage_section(command.actor,section.id)
            module = await self.uow.modules.get_by_id(section.module_id)
            if module is not None:
                module.remove_section(section.id)
                await self.uow.modules.update(module)
            await self.uow.sections.delete(section)
            await self.uow.commit()

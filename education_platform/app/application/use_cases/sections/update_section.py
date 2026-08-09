from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import SectionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.section import Section
from app.domain.entities.user import User
from app.application.interfaces.services.course_access_service import CourseAccessService


@dataclass(slots=True)
class UpdateSectionCommand:
    section_id: UUID
    title: str
    description: str
    position: int
    actor : User


class UpdateSectionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateSectionCommand) -> Section:
        async with self.uow:
            section = await self.uow.sections.get_by_id(command.section_id)
            if section is None:
                raise SectionNotFoundError("Такой секции нет")
            await self.course_access_service.ensure_can_manage_section(command.actor,section.id)
            section.update(
                title=command.title,
                description=command.description,
                position=command.position,
            )
            await self.uow.sections.update(section)
            await self.uow.commit()
            return section

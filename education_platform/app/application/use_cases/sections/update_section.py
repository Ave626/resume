from app.domain.entities.section import Section
from app.application.interfaces.unit_of_work import UnitOfWork
from dataclasses import dataclass
from uuid import UUID,uuid4
from app.application.exceptions import SectionNotFoundError

@dataclass(slots=True)
class UpdateSectionCommand:
    section_id : UUID
    title : str
    description : str
    position : int

class UpdateSectionUseCase:
    def __init__(self,uow : UnitOfWork) -> None:
        self.uow = uow
    
    async def execute(self,command : UpdateSectionCommand) -> Section:
        async with self.uow:
            section = await self.uow.sections.get_by_id(command.section_id)
            if section is None:
                raise SectionNotFoundError("Такой секции нет")
            section.update(
                title = command.title,
                description = command.description,
                position = command.position,
            )
            await self.uow.sections.update(section)
            await self.uow.commit()
            return section


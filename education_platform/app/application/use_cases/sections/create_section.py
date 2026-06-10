from dataclasses import dataclass
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.exceptions import ModuleNotFoundError
from app.domain.entities.section import Section
from uuid import uuid4,UUID

@dataclass(slots=True)
class CreateSectionCommand:
    module_id : UUID
    title : str
    description : str
    position : int

class CreateSectionUseCase:
    def __init__(self,uow : UnitOfWork) -> None:
        self.uow = uow
    
    async def execute(self,command : CreateSectionCommand) -> Section:
        async with self.uow:
            module = await self.uow.modules.get_by_id(command.module_id)
            if module is None:
                raise ModuleNotFoundError("Такого модуля нет")
            section = Section(
                id = uuid4(),
                module_id=module.id,
                title=command.title,
                description=command.description,
                position=command.position,
            )
            module.add_section(section.id)
            await self.uow.sections.add(section)
            await self.uow.modules.update(module)
            await self.uow.commit()
            return section

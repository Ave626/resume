from dataclasses import dataclass
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
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
    def __init__(self,module_repository : ModuleRepository,section_repository : SectionRepository) -> None:
        self.module_repository = module_repository
        self.section_repository = section_repository
    
    async def execute(self,command : CreateSectionCommand) -> Section:
        module = await self.module_repository.get_by_id(command.module_id)
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

        await self.section_repository.add(section)
        await self.module_repository.update(module)
        return section


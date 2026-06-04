from app.application.interfaces.repositories.section_repository import SectionRepository
from app.domain.entities.section import Section
from app.application.exceptions import SectionNotFoundError
from dataclasses import dataclass
from uuid import UUID

@dataclass(slots=True)
class GetSectionQuery:
    section_id : UUID

class GetSectionUseCase:
    def __init__(self,section_repository : SectionRepository) -> None:
        self.section_repository = section_repository
    
    async def execute(self,query : GetSectionQuery) -> Section:
        section = await self.section_repository.get_by_id(query.section_id)
        if section is None:
            raise SectionNotFoundError("Такой секции нет")
        return section

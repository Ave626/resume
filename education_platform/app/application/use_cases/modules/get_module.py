from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import ModuleNotFoundError
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.domain.entities.module import Module


@dataclass(slots=True)
class GetModuleQuery:
    module_id: UUID


class GetModuleUseCase:
    def __init__(self, module_repository: ModuleRepository) -> None:
        self.module_repository = module_repository

    async def execute(self, query: GetModuleQuery) -> Module:
        module = await self.module_repository.get_by_id(query.module_id)
        if module is None:
            raise ModuleNotFoundError("Такого модуля нет")
        return module

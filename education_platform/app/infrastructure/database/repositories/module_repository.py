from uuid import UUID
from app.domain.entities.module import Module
from app.application.interfaces.repositories.module_repository import ModuleRepository
from sqlalchemy.orm import selectinload
from app.infrastructure.database.mappers.module_mapper import ModuleMapper
from app.infrastructure.database.models.module_model import ModuleModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyModuleRepository(ModuleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, module_id) -> Module | None:
        stmt = (
            select(ModuleModel)
            .options(selectinload(ModuleModel.sections))
            .where(ModuleModel.id == str(module_id))
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else ModuleMapper.to_domain(model)

    async def get_by_ids(self, module_ids: list[UUID]) -> list[Module]:
        if not module_ids:
            return []
        stmt = (
            select(ModuleModel)
            .options(selectinload((ModuleModel.sections)))
            .where(ModuleModel.id.in_([str(item) for item in module_ids]))
        )
        result = await self.session.execute(stmt)
        return [ModuleMapper.to_domain(model) for model in result.scalars().all()]

    async def add(self, module: Module) -> None:
        self.session.add(ModuleMapper.to_model(module))
        await self.session.flush()

    async def update(self, module: Module) -> None:
        model = await self.session.get(ModuleModel, str(module.id))
        if model is None:
            return None
        model.title = module.title
        model.description = module.description
        model.position = module.position
        await self.session.flush()
    
    async def delete(self,module : Module) -> None:
        model = await self.session.get(ModuleModel, str(module.id))
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()


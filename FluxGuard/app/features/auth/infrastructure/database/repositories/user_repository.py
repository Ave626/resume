from app.features.auth.application.interfaces.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.domain.entities.user import User
from app.features.auth.application.interfaces.unit_of_work import IAuthUnitOfWork
from uuid import UUID
from app.features.auth.infrastructure.database.mappers.user_mapper import UserMapper
from app.features.auth.infrastructure.database.models.user_model import UserModel
from sqlalchemy import select

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self,session : AsyncSession) -> None:
        self._session = session

    async def get_by_id(self,user_id : UUID) -> User | None:
        model = await self._session.get(UserModel,user_id)
        return UserMapper.to_domain(model) if model else None
    
    async def get_by_email(self,email : str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None
    
    async def add(self,user : User) -> None:
        self._session.add(UserMapper.to_model(user))
        await self._session.flush()
    
    async def delete(self,user : User) -> None:
        model = await self._session.get(UserModel,user.id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

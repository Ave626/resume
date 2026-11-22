from app.core.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.features.auth.application.interfaces.unit_of_work import IAuthUnitOfWork
from app.features.auth.infrastructure.database.repositories.user_repository import SqlAlchemyUserRepository
from typing import Self

class SqlAlchemyAuthUnitOfWork(SqlAlchemyUnitOfWork,IAuthUnitOfWork):
    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self.users = SqlAlchemyUserRepository(self.session)
        return self
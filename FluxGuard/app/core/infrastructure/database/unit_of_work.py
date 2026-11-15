from app.core.application.interfaces.unit_of_work import IUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker
from typing import Self
from types import TracebackType

class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(
        self, session_factory : async_sessionmaker[AsyncSession] | None = None,
        session : AsyncSession | None = None,
    ) -> None:
        self.session_factory = session_factory
        self._external_session = session
        self.session = session
    
    async def __aenter__(self) -> Self:
        if self.session is None:
            if self.session_factory is None:
                raise RuntimeError(
                    "Session factory is required when session is not provided."
                )
            self.session = self.session_factory()
    
        return self
    
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.session is None:
            return
        if exc_type is not None:
            await self.rollback()
        
        if self._external_session is None:
            await self.session.close()
            self.session = None
        
    async def commit(self) -> None:
        if self.session is not None:
            await self.session.commit()
    
    async def rollback(self) -> None:
        if self.session is not None:
            await self.session.rollback()
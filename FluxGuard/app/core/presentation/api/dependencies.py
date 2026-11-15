from app.core.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from collections.abc import AsyncGenerator
from app.core.application.interfaces.unit_of_work import IUnitOfWork
from app.core.infrastructure.database.database import session_factory

async def get_uow() -> AsyncGenerator[IUnitOfWork,None]:
    yield SqlAlchemyUnitOfWork(session_factory=session_factory)

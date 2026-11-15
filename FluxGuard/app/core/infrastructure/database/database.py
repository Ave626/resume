from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker
from app.core.infrastructure.config.settings import settings

engine = create_async_engine(
    pool_size=15,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    url=settings.database_url,echo=settings.DEBUG,
)

session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.infrastructure.broker.taskiq import broker
from app.core.infrastructure.redis.client import redis_client,close_redis
from app.core.infrastructure.database.database import engine
from app.core.presentation.api.handlers.errors import register_exception
from collections.abc import AsyncIterator
from app.features.auth.presentation.api.router import router as auth_router


@asynccontextmanager
async def lifespan(app : FastAPI) -> AsyncIterator[None]:
    if not broker.is_worker_process:
        await broker.startup()
    await redis_client.ping()
    yield
    await close_redis()
    await engine.dispose()
    if not broker.is_worker_process:
        await broker.shutdown()

app = FastAPI(lifespan=lifespan)
register_exception(app)
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

@app.get("/health")
async def root() -> dict:
    return {"status": "ok"}
from app.core.infrastructure.broker.taskiq import broker
from taskiq import TaskiqEvents
from app.core.infrastructure.redis.client import close_redis
from app.core.infrastructure.database.database import engine
import logging

logger = logging.getLogger("worker")

@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup():
    logger.info("Запуск воркера")


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown():
    await close_redis()
    await engine.dispose()

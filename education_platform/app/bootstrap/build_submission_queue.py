from functools import lru_cache
from redis.asyncio import Redis
from app.application.interfaces.submissiion_queue import SubmissionQueue
from app.infrastructure.config.settings import get_settings
from app.infrastructure.queues.redis_submission_queues import RedisSubmissionQueue


import asyncio

_redis_clients: dict[asyncio.AbstractEventLoop, Redis] = {}


def get_redis_client() -> Redis:
    settings = get_settings()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return Redis.from_url(settings.redis_url)

    if loop not in _redis_clients:
        _redis_clients[loop] = Redis.from_url(settings.redis_url)
    return _redis_clients[loop]


@lru_cache(maxsize=1)
def build_submission_queue() -> SubmissionQueue:
    settings = get_settings()
    return RedisSubmissionQueue(
        client=get_redis_client(), queue_name=settings.submission_queue_name
    )

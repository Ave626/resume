from redis.asyncio import ConnectionPool, Redis
from app.core.infrastructure.config.settings import settings

redis_pool = ConnectionPool.from_url(
    settings.redis_url,
    max_connections=100,
    socket_timeout=1.0,
    socket_connect_timeout=1.0,
    decode_responses=True,
)

redis_client = Redis(connection_pool=redis_pool)

async def get_redis() -> Redis:
    return redis_client

async def close_redis() -> None:
    await redis_client.aclose()
    await redis_pool.disconnect()
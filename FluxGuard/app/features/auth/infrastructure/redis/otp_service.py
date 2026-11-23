from redis.asyncio import Redis
from app.features.auth.application.interfaces import IOtpService


class RedisOtpService(IOtpService):
    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def save(self, email: str, code: str, ex: int) -> None:
        await self._redis.set(f"otp:{email}", code, ex=ex)

    async def get_code(self, email: str) -> str | None:
        code = await self._redis.get(f"otp:{email}")
        return code

    async def delete(self, email: str) -> None:
        await self._redis.delete(f"otp:{email}")

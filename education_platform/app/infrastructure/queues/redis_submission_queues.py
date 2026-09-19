from uuid import UUID
from redis.asyncio import Redis
from app.application.interfaces.submissiion_queue import SubmissionQueue


class RedisSubmissionQueue(SubmissionQueue):
    def __init__(self, client: Redis, queue_name: str) -> None:
        self.client = client
        self.queue_name = queue_name

    async def enqueue(self, submission_id: UUID) -> None:
        await self.client.rpush(self.queue_name, str(submission_id))

    async def dequeue(self) -> UUID:
        result = await self.client.blpop(self.queue_name, timeout=0)
        if result is None:
            raise RuntimeError('Redis queue returned no message.')

        _, raw_submission_id = result
        return UUID(raw_submission_id.decode('utf-8'))
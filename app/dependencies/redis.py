from typing import AsyncGenerator

from redis.asyncio import Redis

from app.core.redis import RedisClient


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    yield RedisClient

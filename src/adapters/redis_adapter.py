import logging
from datetime import timedelta

from redis import RedisError
from redis.asyncio import Redis

from src.core.config import redis_config
from src.utils.exception_decorator import catch_exceptions
from src.utils.json_serialization import deserialize_json, serialize_json

logger = logging.getLogger(__name__)


class RedisRequestCachingService:
    prefix = "request-cache:"

    def __init__(self, redis: Redis):
        self.redis = redis

    @catch_exceptions((RedisError,))
    async def get_cache(self, key: str) -> dict | None:
        if response := await self.redis.get(self.prefix + key):
            return deserialize_json(response)

    @catch_exceptions((RedisError, TypeError))
    async def set_cache(
        self,
        key: str,
        response: dict,
        expire: timedelta = redis_config.CACHE_EXPIRE_TIME,
    ) -> None:
        await self.redis.setex(self.prefix + key, expire, serialize_json(response))

    @catch_exceptions((RedisError,))
    async def remove_all_cache(self, key_substring: str) -> None:
        keys = await self.redis.keys(f"*{key_substring}*")
        if len(keys):
            await self.redis.delete(*keys)

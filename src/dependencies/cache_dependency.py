from redis.asyncio import Redis

from src.adapters.redis_adapter import RedisRequestCachingService
from src.dependencies.redis_dependency import get_redis


def get_redis_request_caching_service() -> RedisRequestCachingService:
    return RedisRequestCachingService(get_redis())

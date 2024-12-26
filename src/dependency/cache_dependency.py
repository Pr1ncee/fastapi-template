from redis.asyncio import Redis

from src.dependency.redis_dependency import get_redis
from src.adapters.redis_adapter import RedisRequestCachingService


def get_redis_request_caching_service(
    redis: Redis = None,
) -> RedisRequestCachingService:
    if redis is None:
        redis = get_redis()
    return RedisRequestCachingService(redis)

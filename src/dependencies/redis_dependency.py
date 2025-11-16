from redis.asyncio import Redis

from src.core.config import redis_config


def get_redis() -> Redis:
    return Redis(host=redis_config.HOST, port=redis_config.PORT, decode_responses=True)

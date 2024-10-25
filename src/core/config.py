import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class GeneralConfig:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(',')
    CORS_METHODS = os.getenv("CORS_METHODS", "").split(',')
    CORS_HEADERS = os.getenv("CORS_HEADERS", "").split(',')
    ANONYMOUS_ENDPOINTS = [
        "/api/v1/health-check/",
        "/api/docs",
        "/favicon.ico",
        "/api/openapi.json",
        "api/docs",
        "/api/v1/user/sign-in",
        "/api/v1/user/sign-up",
        "/api/v1/user/confirm-sign-in",
    ]
    LRU_CACHE_MAX_SIZE = 16
    REDIS_CACHE_EXPIRE_TIME = timedelta(minutes=10)


class JWTConfig:
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "")
    JWT_EXP_MIN = os.getenv("JWT_EXP_MIN", 180)
    JWT_REFRESH_EXP_MIN = os.getenv("JWT_EXP_MIN", 720)


class PostgresConfig:
    HOST = os.getenv("POSTGRES_HOST", "localhost")
    PWD = os.getenv("POSTGRES_PASSWORD", "postgres")
    USER = os.getenv("POSTGRES_USER", "postgres")
    NAME = os.getenv("POSTGRES_DB", "postgres")
    PORT = os.getenv("POSTGRES_PORT", "5432")
    ASYNC_URL = f"postgresql+asyncpg://{USER}:{PWD}@{HOST}:{PORT}/{NAME}"


class RedisConfig:
    HOST = os.getenv("REDIS_HOST", "redis")
    PORT = int(os.getenv("REDIS_PORT", 6379))


general_config = GeneralConfig()
postgres_config = PostgresConfig()
jwt_config = JWTConfig()
redis_config = RedisConfig()
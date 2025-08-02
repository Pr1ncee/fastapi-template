import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class GeneralConfig:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
    CORS_METHODS = os.getenv("CORS_METHODS", "").split(",")
    CORS_HEADERS = os.getenv("CORS_HEADERS", "").split(",")
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
    LRU_CACHE_MAX_SIZE = 16  # In bytes


class JWTConfig:
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "")
    JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "180"))
    JWT_REFRESH_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "720"))


class PostgresConfig:
    CONN_STRING = os.getenv("POSTGRES_CONN_STRING", "")


class RedisConfig:
    HOST = os.getenv("REDIS_HOST", "redis")
    PORT = int(os.getenv("REDIS_PORT", "6379"))
    CACHE_TTL = timedelta(seconds=int(os.getenv("REDIS_TTL", "300")))  # In seconds


general_config = GeneralConfig()
postgres_config = PostgresConfig()
jwt_config = JWTConfig()
redis_config = RedisConfig()

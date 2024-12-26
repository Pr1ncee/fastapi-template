from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from src.api.middlewares.auth_middleware import AuthenticationMiddleware
from src.api.middlewares.cache_middleware import CacheMiddleware
from src.api.router import router
from src.core.config import general_config, redis_config
from src.core.exceptions.exception_handlers.middleware_exception_handlers import (
    authentication_error_exception_handler,
)

from src.core.logger import setup_logger
from src.dependency.cache_dependency import get_redis_request_caching_service

setup_logger()

api_prefix = "/api"


middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=general_config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=general_config.CORS_METHODS,
        allow_headers=general_config.CORS_HEADERS,
    ),
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
    Middleware(
        AuthenticationMiddleware, on_error=authentication_error_exception_handler
    ),
    Middleware(
        CacheMiddleware,
        caching_repository=get_redis_request_caching_service(),
        expire=redis_config.CACHE_EXPIRE_TIME,
    ),
]

app = FastAPI(
    title="FastAPI Template",
    middleware=middlewares,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    debug=True,
    version="0.0.1",
)
app.openapi_version = "3.0.2"

add_pagination(app)
app.include_router(router, prefix=api_prefix)

from src.core.exceptions.exception_handlers.core_exception_handlers import *  # noqa

import logging
from datetime import timedelta
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.status import HTTP_200_OK

from src.core.config import redis_config
from src.enums.http_method_enum import HTTPMethodEnum
from src.adapters.redis_adapter import RedisRequestCachingService

logger = logging.getLogger(__name__)

class CacheMiddleware(BaseHTTPMiddleware):
    auth_scheme = HTTPBearer(auto_error=False)

    def __init__(
        self,
        app: FastAPI,
        caching_repository: RedisRequestCachingService,
        expire: timedelta = redis_config.CACHE_EXPIRE_TIME,
    ) -> None:
        self.caching_repository = caching_repository
        self.expire = expire
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        if request.method.lower() != HTTPMethodEnum.GET.value:
            return await call_next(request)

        if not (authorization := await self.auth_scheme(request)):
            return await call_next(request)

        path = f"{request.url.path}/{request.url.query}"
        cache_key = f"{path}:{authorization.credentials}"
        extra = {"path": path}

        cached_response = await self.caching_repository.get_cache(cache_key)
        if cached_response:
            logger.info("Returning cached response", extra=extra)
            return Response(
                content=cached_response["content"],
                media_type="application/json",
                status_code=cached_response["status_code"],
            )

        logger.info("Cached response not found! Processing with the actual handler", extra=extra)
        response = await call_next(request)  # Cache miss: Proceed with the request to the actual handler

        if response.status_code == HTTP_200_OK:
            response_body = [chunk async for chunk in response.body_iterator]
            response_dict = {
                "content": b"".join(response_body).decode("utf-8"),
                "status_code": response.status_code,
            }

            # Serialize and store the response in cache
            logger.info("Caching the request", extra=extra)
            await self.caching_repository.set_cache(
                cache_key, response_dict, self.expire
            )
            return Response(
                content=response_dict["content"],
                media_type="application/json",
                status_code=response.status_code,
            )
        return response

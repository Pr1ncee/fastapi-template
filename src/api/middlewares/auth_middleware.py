import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from fastapi import Request as FastAPIRequest
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from starlette_context import context

from src.core.config import general_config
from src.core.exceptions import AuthenticationError
from src.services.auth_service import AuthService

if TYPE_CHECKING:
    from starlette.requests import Request

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    auth_scheme = HTTPBearer(auto_error=False)

    def __init__(self, on_error: Callable, app: ASGIApp) -> None:
        self.on_error = on_error
        super().__init__(app)

    async def dispatch(self, request: FastAPIRequest, call_next: Callable) -> Response:
        authorization: HTTPAuthorizationCredentials | None = await self.auth_scheme(request)
        if request.url.path in general_config.ANONYMOUS_ENDPOINTS:
            return await call_next(request)
        try:
            if authorization:
                user_info = AuthService.decode_token(token=authorization.credentials)

                # Setting a global context that will be accessible across the app
                context["request"] = request
                context["user_info"] = user_info
                context["access_token"] = authorization.credentials
                logger.info("The user has been successfully authenticated", extra={"user": user_info})
                return await call_next(request)
            else:
                logger.error("Authorization failed! No token")
                raise AuthenticationError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"message": "No Token"},
                )
        except AuthenticationError as e:
            logger.exception("Got error while authenticating the user", extra={"e": e})
            return self.on_error(request=request, exc=e)

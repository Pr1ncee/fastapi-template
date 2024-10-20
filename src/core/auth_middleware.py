import logging

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from starlette_context import context

from src.core.config import general_config
from src.core.exceptions import AuthenticationError
from src.services.jwt_service import JWTService

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    auth_scheme = HTTPBearer(auto_error=False)

    def __init__(self, on_error, app: ASGIApp):
        self.on_error = on_error
        super().__init__(app)

    async def dispatch(self, request, call_next):
        authorization: HTTPAuthorizationCredentials = await self.auth_scheme(request)
        if request.url.path in general_config.ANONYMOUS_ENDPOINTS:
            response = await call_next(request)
            return response
        try:
            if authorization:
                user_info = JWTService.decode_token(token=authorization.credentials)

                # Setting a global context that will be accessible across the app
                context["request"]: Request = request
                context["user_info"] = user_info
                context["access_token"]: str = authorization.credentials
                response = await call_next(request)
                return response

            else:
                raise AuthenticationError(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "No Token"})
        except AuthenticationError as exc:
            return self.on_error(request=request, exc=exc)
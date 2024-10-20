from starlette import status
from starlette.authentication import AuthenticationError as StarletteAuthenticationError


class BaseError(Exception):
    status_code: int
    content: dict

    def __init__(self, status_code: int = None, content: dict = None):
        self.status_code = status_code or self.status_code
        self.content = content or self.content


class ClientError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    content = {"message": "The request failed!"}


class ServerError(BaseError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    content = {"message": "Server error!"}


class AuthenticationError(StarletteAuthenticationError, BaseError):
    status_code = status.HTTP_401_UNAUTHORIZED

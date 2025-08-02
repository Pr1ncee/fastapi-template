import logging

import jwt
from starlette import status

from src.core.config import jwt_config
from src.core.exceptions.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    async def decode_token(token: str, verify_expiration: bool = True) -> dict:
        try:
            return jwt.decode(
                jwt=token,
                key=jwt_config.JWT_SECRET_KEY,
                algorithms=[jwt_config.JWT_ALGORITHM],
                options={"verify_exp": verify_expiration},
            )
        except jwt.ExpiredSignatureError as e:
            logger.exception("The token is expired!", extra={"e": e})
            raise AuthenticationError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Token Expired"},
            ) from e
        except BaseException as e:
            logger.exception("The token is invalid! Got the error when getting payload", extra={"e": e})
            raise AuthenticationError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Authorization Failed"},
            ) from e

    @staticmethod
    async def encode_token(payload: dict) -> str:
        return jwt.encode(payload, jwt_config.JWT_SECRET_KEY, algorithm=jwt_config.JWT_ALGORITHM)

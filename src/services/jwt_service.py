import jwt
from starlette import status

from src.core.config import jwt_config
from src.core.exceptions.exceptions import AuthenticationError


class JWTService:
    @staticmethod
    async def decode_token(
            token: str,
            secret_key: str = jwt_config.JWT_SECRET_KEY,
            verify_expiration: bool = True
    ) -> dict:
        try:
            return jwt.decode(
                jwt=token,
                key=secret_key,
                algorithms=[jwt_config.JWT_ALGORITHM],
                options={"verify_exp": verify_expiration}
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Token Expired"})
        except BaseException:
            raise AuthenticationError(
                status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Authorization Failed"}
            )

    @staticmethod
    async def encode_token(payload: dict, secret_key: str = jwt_config.JWT_SECRET_KEY) -> str:
        return jwt.encode(payload, secret_key, algorithm=jwt_config.JWT_ALGORITHM)

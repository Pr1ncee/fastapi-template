from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core.exceptions.exceptions import AuthenticationError


def authentication_error_exception_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.content)

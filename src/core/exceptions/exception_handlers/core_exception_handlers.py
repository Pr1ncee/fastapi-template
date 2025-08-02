from fastapi import Request, status
from pydantic import ValidationError as PydanticValidationError
from starlette.responses import JSONResponse

from src.core.exceptions.exceptions import (
    ClientError,
    ServerError,
)
from src.main import app


@app.exception_handler(PydanticValidationError)
async def validation_exception_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Provided values not valid.", "metadata": f"{exc}"},
    )


@app.exception_handler(ClientError)
async def client_error_exception_handler(request: Request, exc: ClientError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.content)


@app.exception_handler(ServerError)
async def server_error_exception_handler(request: Request, exc: ServerError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.content)

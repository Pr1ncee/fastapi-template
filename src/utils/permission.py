from collections.abc import Callable
from functools import wraps

from fastapi import HTTPException
from starlette import status
from starlette_context import context


def permission(permissions: list) -> Callable:
    def outer_wrapper(function: Callable) -> Callable:
        @wraps(function)
        async def inner_wrapper(*args, **kwargs) -> Callable | None:
            user = context["user"]
            if not any(permission in list(permissions) for permission in user.permissions):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Allowed")
            return await function(*args, **kwargs)

        return inner_wrapper

    return outer_wrapper

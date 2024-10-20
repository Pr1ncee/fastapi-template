from functools import wraps

from fastapi import HTTPException
from starlette import status
from starlette_context import context


def permission(permissions: list):
    def outer_wrapper(function):
        @wraps(function)
        async def inner_wrapper(*args, **kwargs):
            user = context["user"]
            if not any(permission in [perm for perm in permissions] for permission in user.permissions):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Allowed")
            return await function(*args, **kwargs)
        return inner_wrapper
    return outer_wrapper

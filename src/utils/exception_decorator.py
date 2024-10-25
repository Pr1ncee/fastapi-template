import asyncio
import logging
from functools import wraps
from typing import Callable, Coroutine

logger = logging.getLogger(__name__)


def catch_exceptions(exceptions: tuple) -> Callable:
    def decorator(func: Callable) -> Callable:
        """
        Can be used with both async and sync functions to catch exceptions with specified exceptions

        Example usage:
            @catch_exceptions((ValueError, TypeError))
            [async] def func():
                ...

        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> dict | Coroutine | None:
            error_msg = "Got error: <{0}> when calling function <{1}>"
            if asyncio.iscoroutinefunction(func):  # Handling async functions
                async def async_wrapper() -> Callable | None:
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        logger.exception(error_msg.format(e, func.__name__))
                return async_wrapper()

            try:  # Handling sync functions
                return func(*args, **kwargs)
            except exceptions as e:
                logger.exception(error_msg.format(e, func.__name__))
        return wrapper
    return decorator

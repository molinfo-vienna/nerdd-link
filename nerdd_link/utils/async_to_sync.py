import asyncio
from functools import wraps

__all__ = ["async_to_sync"]


def async_to_sync(func):
    """
    A decorator to convert an async function to a sync function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper

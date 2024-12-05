import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

__all__ = ["async_to_sync"]

T = TypeVar("T")


def async_to_sync(func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """
    A decorator to convert an async function to a sync function.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()
        # Check if the loop is already running
        if loop.is_running():
            # If in an already running event loop, create a new task
            return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), loop).result()
        else:
            # Run the async function in the event loop
            return loop.run_until_complete(func(*args, **kwargs))

    return wrapper

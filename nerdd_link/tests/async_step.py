import asyncio
from functools import wraps


def async_step(step):
    """Convert an async step function to a normal one."""

    @wraps(step)
    def run_step(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(step(*args, **kwargs))

    return run_step

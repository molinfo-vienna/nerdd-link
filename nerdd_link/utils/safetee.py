from itertools import tee
from threading import Lock

__all__ = ["safetee"]

# Note: This code was taken from https://stackoverflow.com/questions/6703594


class safeteeobject:
    """tee object wrapped to make it thread-safe"""

    def __init__(self, teeobj, lock):
        self.teeobj = teeobj
        self.lock = lock

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.teeobj)

    def __copy__(self):
        return safeteeobject(self.teeobj.__copy__(), self.lock)


def safetee(iterable, n=2):
    """tuple of n independent thread-safe iterators"""
    lock = Lock()
    return tuple(safeteeobject(teeobj, lock) for teeobj in tee(iterable, n))

from itertools import tee
from threading import Lock
from typing import Generic, Iterable, Iterator, Protocol, Tuple, TypeVar, cast

__all__ = ["safetee"]


T = TypeVar("T")


class Tee(Protocol, Iterator[T]):
    def __copy__(self) -> "Tee[T]": ...


# Note: This code was taken from https://stackoverflow.com/questions/6703594


class safeteeobject(Generic[T]):
    """tee object wrapped to make it thread-safe"""

    def __init__(self, teeobj: Tee[T], lock: Lock) -> None:
        self.teeobj = teeobj
        self.lock = lock

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        with self.lock:
            return next(self.teeobj)

    def __copy__(self) -> "safeteeobject[T]":
        return safeteeobject(self.teeobj.__copy__(), self.lock)


def safetee(iterable: Iterable[T], n: int = 2) -> Tuple[safeteeobject[T], ...]:
    """tuple of n independent thread-safe iterators"""
    lock = Lock()
    return tuple(safeteeobject(cast(Tee[T], teeobj), lock) for teeobj in tee(iterable, n))

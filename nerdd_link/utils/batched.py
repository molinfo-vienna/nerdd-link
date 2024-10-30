from itertools import islice
from typing import Iterable, Iterator, List, TypeVar

__all__ = ["batched"]

T = TypeVar("T")


def batched(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """
    Batch an iterable into chunks of size `size`.

    Args:
        iterable: The iterable to batch.
        size: The size of each batch.

    Returns:
        An iterator over the batches.
    """
    assert size > 0, "Size must be greater than 0"

    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, size))
        if not batch:
            return
        yield batch

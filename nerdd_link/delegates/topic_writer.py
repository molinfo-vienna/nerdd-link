from asyncio import Queue
from typing import Iterable

from nerdd_module import Writer

__all__ = ["TopicWriter"]


class TopicWriter(Writer, output_format="json"):
    def __init__(
        self,
        queue: Queue,
    ):
        self._queue = queue

    def write(self, records: Iterable[dict]) -> None:
        for record in records:
            self._queue.put_nowait(record)
        self._queue.put_nowait(None)

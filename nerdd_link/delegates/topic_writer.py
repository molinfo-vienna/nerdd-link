from multiprocessing import Queue
from typing import Iterable

from nerdd_module import Writer, WriterConfig

__all__ = ["TopicWriter"]


class TopicWriter(Writer):
    def __init__(
        self,
        queue: Queue,
    ):
        self._queue = queue

    def write(self, records: Iterable[dict]) -> None:
        for record in records:
            self._queue.put(record)
        self._queue.put(None)

    config = WriterConfig(output_format="json")

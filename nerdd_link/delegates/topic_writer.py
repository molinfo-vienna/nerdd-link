from asyncio import AbstractEventLoop, Queue, run_coroutine_threadsafe
from typing import Iterable

from nerdd_module import Writer, WriterConfig

__all__ = ["TopicWriter"]


class TopicWriter(Writer):
    def __init__(self, queue: Queue, loop: AbstractEventLoop):
        self._queue = queue
        self._loop = loop

    def write(self, records: Iterable[dict]) -> None:
        for record in records:
            run_coroutine_threadsafe(self._queue.put(record), self._loop)
        run_coroutine_threadsafe(self._queue.put(None), self._loop)

    config = WriterConfig(output_format="json")

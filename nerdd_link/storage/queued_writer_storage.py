import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, BinaryIO, Iterator, Literal, Optional, Union

from .storage import Storage

__all__ = ["QueuedWriterStorage"]


class _QueuedWriteBuffer:
    """Lightweight in-memory write buffer for queued file writing without RLock overhead."""

    def __init__(
        self,
        storage: Storage,
        identifier: str,
        executor: ThreadPoolExecutor,
        futures: list[Future[None]],
    ) -> None:
        self._storage = storage
        self._identifier = identifier
        self._executor = executor
        self._futures = futures
        self._buffer = bytearray()
        self.closed = False

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def flush(self) -> None:
        pass

    def write(self, data: Union[bytes, str, memoryview]) -> int:
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        if isinstance(data, str):
            encoded = data.encode("utf-8")
            self._buffer.extend(encoded)
            return len(encoded)
        self._buffer.extend(data)
        return len(data)

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        data = bytes(self._buffer)
        future = self._executor.submit(self._do_write, data)
        self._futures.append(future)

    def _do_write(self, data: bytes) -> None:
        with self._storage._get_binary_file_handle(self._identifier, mode="wb") as f:
            f.write(data)

    def __enter__(self) -> "_QueuedWriteBuffer":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


class QueuedWriterStorage(Storage):
    """Storage decorator that queues file writes and executes them asynchronously."""

    def __init__(self, storage: Storage, max_workers: int = 10) -> None:
        super().__init__(storage._prefix)
        self._storage = storage
        self._max_workers = max_workers
        self._executor: Optional[ThreadPoolExecutor] = ThreadPoolExecutor(max_workers=max_workers)
        self._futures: list[Future[None]] = []

    def _validate(self) -> None:
        self._storage.validate()

    def _unprefix_file_path(self, file_path: str) -> str:
        return self._storage._unprefix_file_path(file_path)

    def _iter_directory(self, identifier: str) -> Iterator[str]:
        return self._storage._iter_directory(identifier)

    def _file_exists(self, identifier: str) -> bool:
        return self._storage._file_exists(identifier)

    def _get_file_size(self, identifier: str) -> int:
        return self._storage._get_file_size(identifier)

    def _get_binary_file_handle(self, identifier: str, mode: Literal["rb", "wb"]) -> BinaryIO:
        if mode == "wb":
            if self._executor is None:
                self._executor = ThreadPoolExecutor(max_workers=self._max_workers)
            return _QueuedWriteBuffer(  # type: ignore[return-value]
                self._storage, identifier, self._executor, self._futures
            )
        return self._storage._get_binary_file_handle(identifier, mode)

    def _delete_file(self, identifier: str) -> None:
        self._storage._delete_file(identifier)

    def flush(self) -> None:
        """Wait for all pending writes to complete and shut down worker threads."""
        try:
            for future in self._futures:
                future.result()
            self._futures.clear()
        finally:
            if self._executor is not None:
                self._executor.shutdown(wait=True)
                self._executor = None

    async def aflush(self) -> None:
        """Wait asynchronously for all pending writes to complete."""
        await asyncio.to_thread(self.flush)

    def close(self) -> None:
        self.flush()

    def __enter__(self) -> "QueuedWriterStorage":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    async def __aenter__(self) -> "QueuedWriterStorage":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aflush()

    def __repr__(self) -> str:
        return f"QueuedWriterStorage({self._storage!r})"

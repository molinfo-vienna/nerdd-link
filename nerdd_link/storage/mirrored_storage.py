import io
from typing import Any, BinaryIO, Iterator, List, Literal, Optional, Sequence, cast

from .storage import Storage

__all__ = ["MirroredStorage"]


class _MirroredWriteRawIO(io.RawIOBase):
    def __init__(self, handles: Sequence[BinaryIO]) -> None:
        super().__init__()
        self._handles = handles

    def writable(self) -> bool:
        return True

    def write(self, buffer: Any) -> int:
        if self.closed:
            raise ValueError("write to closed file")

        view = memoryview(buffer)
        errors: List[Exception] = []
        for handle in self._handles:
            try:
                self._write_all(handle, view)
            except Exception as error:
                errors.append(error)

        if errors:
            raise errors[0]
        return len(view)

    def flush(self) -> None:
        if self.closed:
            raise ValueError("flush of closed file")

        errors: List[Exception] = []
        for handle in self._handles:
            try:
                handle.flush()
            except Exception as error:
                errors.append(error)

        if errors:
            raise errors[0]

    def close(self) -> None:
        if self.closed:
            return

        errors: List[Exception] = []
        try:
            super().close()
        except Exception as error:
            errors.append(error)

        for handle in self._handles:
            try:
                handle.close()
            except Exception as error:
                errors.append(error)

        self._handles = ()
        if not self.closed:
            try:
                super().close()
            except Exception as error:
                errors.append(error)

        if errors:
            raise errors[0]

    def _write_all(self, handle: BinaryIO, buffer: memoryview) -> None:
        offset = 0
        while offset < len(buffer):
            written = handle.write(buffer[offset:])
            if written is None or written <= 0 or written > len(buffer) - offset:
                raise OSError("Storage backend did not accept the complete write.")
            offset += written


class MirroredStorage(Storage):
    """Storage that reads from ordered backends and writes to every backend."""

    def __init__(self, *storages: Storage) -> None:
        if not storages:
            raise ValueError("MirroredStorage requires at least one storage instance.")

        super().__init__(storages[0]._prefix)
        self._storages = storages

    def _iter_directory(self, identifier: str) -> Iterator[str]:
        seen = set()
        for storage in self._storages:
            for file_identifier in storage._iter_directory(identifier):
                if file_identifier not in seen:
                    seen.add(file_identifier)
                    yield file_identifier

    def _file_exists(self, identifier: str) -> bool:
        return any(storage._file_exists(identifier) for storage in self._storages)

    def _get_binary_file_handle(self, identifier: str, mode: Literal["rb", "wb"]) -> BinaryIO:
        # when reading, return the first backend that has the file
        if mode == "rb":
            for storage in self._storages:
                if storage._file_exists(identifier):
                    return storage._get_binary_file_handle(identifier, mode)

            # fail with the error raised by the first storage
            return self._storages[0]._get_binary_file_handle(identifier, mode)
        else:  # mode == "wb", write to all backends
            handles: List[BinaryIO] = []
            first_error: Optional[Exception] = None
            for storage in self._storages:
                try:
                    handles.append(storage._get_binary_file_handle(identifier, mode))
                except Exception as error:
                    if first_error is None:
                        first_error = error

            if first_error is not None:
                for handle in handles:
                    try:
                        handle.close()
                    except Exception:
                        pass
                raise first_error

            return cast(BinaryIO, _MirroredWriteRawIO(handles))

    def _delete_file(self, identifier: str) -> None:
        errors: List[Exception] = []
        for storage in self._storages:
            try:
                storage._delete_file(identifier)
            except Exception as error:
                errors.append(error)

        if errors:
            raise errors[0]

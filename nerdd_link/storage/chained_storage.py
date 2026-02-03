from typing import BinaryIO, Iterator, Literal

from .storage import Storage

__all__ = ["ChainedStorage"]


class ChainedStorage(Storage):
    """Storage that reads from ordered backends and writes to the first backend."""

    def __init__(self, *storages: Storage) -> None:
        if not storages:
            raise ValueError("ChainedStorage requires at least one storage instance.")

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
        primary = self._storages[0]
        if mode == "wb":
            return primary._get_binary_file_handle(identifier, mode)

        for storage in self._storages:
            if storage._file_exists(identifier):
                return storage._get_binary_file_handle(identifier, mode)

        # fail with the error raised by the primary storage
        return primary._get_binary_file_handle(identifier, mode)

    def _delete_file(self, identifier: str) -> None:
        for storage in self._storages:
            storage._delete_file(identifier)

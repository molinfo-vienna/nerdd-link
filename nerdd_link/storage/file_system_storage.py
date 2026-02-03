import os
import posixpath
from typing import IO, Iterator

from .storage import Storage

__all__ = ["FileSystemStorage"]


class FileSystemStorage(Storage):
    def __init__(self, root_path: str) -> None:
        super().__init__("file")
        self.root_path = root_path

    def _iter_directory(self, identifier: str) -> Iterator[str]:
        directory_path = self._resolve_file_path(identifier)
        if not os.path.isdir(directory_path):
            return

        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file():
                    yield posixpath.join(identifier, entry.name)

    def _resolve_file_path(self, identifier: str) -> str:
        return os.path.join(self.root_path, *identifier.split("/"))

    def _file_exists(self, identifier: str) -> bool:
        return os.path.exists(self._resolve_file_path(identifier))

    def _get_file_handle(self, identifier: str, mode: str) -> IO:
        file_path = self._resolve_file_path(identifier)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return open(file_path, mode)

    def _delete_file(self, identifier: str) -> None:
        file_path = self._resolve_file_path(identifier)
        if os.path.exists(file_path):
            os.remove(file_path)

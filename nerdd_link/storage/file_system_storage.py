from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator, Literal

from .storage import Storage

__all__ = ["FileSystemStorage"]


class FileSystemStorage(Storage):
    def __init__(self, root_path: str) -> None:
        super().__init__("file")
        self.root_path = root_path

    def _validate(self) -> None:
        root_path = Path(self.root_path)
        try:
            root_path.mkdir(parents=True, exist_ok=True)
        except FileExistsError as error:
            raise ValueError(f"Storage root path is not a directory: {self.root_path!r}") from error
        except OSError as error:
            raise ValueError(f"Could not create storage root path: {self.root_path!r}") from error

    def _iter_directory(self, identifier: str) -> Iterator[str]:
        directory_path = self._resolve_file_path(identifier)
        if not directory_path.is_dir():
            return

        for entry in directory_path.iterdir():
            if entry.is_file():
                yield str(PurePosixPath(identifier) / entry.name)

    def _resolve_file_path(self, identifier: str) -> Path:
        return Path(self.root_path).joinpath(*identifier.split("/"))

    def _file_exists(self, identifier: str) -> bool:
        return self._resolve_file_path(identifier).exists()

    def _get_binary_file_handle(self, identifier: str, mode: Literal["rb", "wb"]) -> BinaryIO:
        file_path = self._resolve_file_path(identifier)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path.open(mode)

    def _delete_file(self, identifier: str) -> None:
        self._resolve_file_path(identifier).unlink(missing_ok=True)

    def __repr__(self) -> str:
        return f"FileSystemStorage({self.root_path!r})"

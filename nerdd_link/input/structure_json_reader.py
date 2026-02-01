import json
from typing import Iterator, Optional, Protocol

from nerdd_module.input import ExploreCallable, MoleculeEntry, Reader

from ..storage import Storage

__all__ = ["StructureJsonReader"]


# TODO: move somewhere else
class StreamLike(Protocol):
    def read(self, size: int = -1) -> str: ...

    def seek(self, offset: int, whence: int = 0) -> int: ...


class StructureJsonReader(Reader):
    def __init__(self, storage: Optional[Storage] = None) -> None:
        super().__init__()
        self._storage = storage

    def read(self, input_stream: StreamLike, explore: ExploreCallable) -> Iterator[MoleculeEntry]:
        if not hasattr(input_stream, "read") or not hasattr(input_stream, "seek"):
            raise TypeError("input must be a stream-like object")

        input_stream.seek(0)

        contents = json.load(input_stream)

        if self._storage is None:
            raise ValueError("Storage must be provided to read from a JSON file")

        assert isinstance(contents, list) and all(
            (isinstance(entry, dict) and "id" in entry.keys()) for entry in contents
        )

        for entry in contents:
            source_id = entry.get("id", None)
            handle = self._storage.get_source_file_handle(source_id, "rb")
            yield from explore(handle)

    def __repr__(self) -> str:
        return f"StructureJsonReader(storage={self._storage})"

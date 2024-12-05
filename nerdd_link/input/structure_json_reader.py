import json
from typing import Iterator, Protocol

from nerdd_module.input import ExploreCallable, MoleculeEntry, Reader

__all__ = ["StructureJsonReader"]


class StreamLike(Protocol):
    def read(self, size: int = -1) -> str: ...

    def seek(self, offset: int, whence: int = 0) -> int: ...


class StructureJsonReader(Reader):
    def __init__(self) -> None:
        super().__init__()

    def read(self, input_stream: StreamLike, explore: ExploreCallable) -> Iterator[MoleculeEntry]:
        if not hasattr(input_stream, "read") or not hasattr(input_stream, "seek"):
            raise TypeError("input must be a stream-like object")

        input_stream.seek(0)

        contents = json.load(input_stream)

        assert isinstance(contents, list) and all(
            (isinstance(entry, dict) and "id" in entry.keys()) for entry in contents
        )

        for entry in contents:
            source_id = entry.get("id", None)
            filename = entry.get("filename", None)
            for result in explore(source_id):
                source = result.source
                if len(source) > 0 and source[0] == source_id:
                    result._replace(source=(filename, *source[1:]))
                yield result

    def __repr__(self) -> str:
        return "StructureJsonReader()"

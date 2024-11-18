import json
from collections.abc import Generator

from nerdd_module.input import MoleculeEntry, Reader

__all__ = ["StructureJsonReader"]


class StructureJsonReader(Reader):
    def __init__(self):
        super().__init__()

    def read(self, input_stream, explore) -> Generator[MoleculeEntry, None, None]:
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
                    result._replace(source=tuple(filename, *source[1:]))
                yield result

    def __repr__(self) -> str:
        return "StructureJsonReader()"

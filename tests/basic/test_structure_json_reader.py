import io
import json
from typing import IO, Any, Iterator

from nerdd_module.input import MoleculeEntry

from nerdd_link.input import StructureJsonReader


class DummyStorage:
    def get_source_file_handle(self, source_id: str, mode: str) -> IO[bytes]:
        assert mode == "rb"
        # return a byte stream (content is not important for this test)
        return io.BytesIO(b"some content")


# an explore callable that will always return 5 dummy entries
def dummy_explore(_: Any) -> Iterator[MoleculeEntry]:
    for _ in range(5):
        yield MoleculeEntry("value", "test", ("raw_input",), None, [])


def test_prepends_filename_to_every_source() -> None:
    input_stream = io.StringIO(json.dumps([{"id": "source-1", "filename": "input.smi"}]))

    entries = list(StructureJsonReader(DummyStorage()).read(input_stream, dummy_explore))

    assert all(entry.source == ("input.smi",) for entry in entries)


def test_leaves_sources_unchanged_without_filename() -> None:
    contents = [{"id": "source-1", "filename": None}, {"id": "source-2"}]
    input_stream = io.StringIO(json.dumps(contents))

    entries = list(StructureJsonReader(DummyStorage()).read(input_stream, dummy_explore))

    assert all(entry.source == ("raw_input",) for entry in entries)

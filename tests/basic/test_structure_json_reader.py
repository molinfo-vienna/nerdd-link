import io
import json
from typing import Any, Iterator

import pytest
from nerdd_module.input import MoleculeEntry
from nerdd_module.input.depth_first_explorer import InvalidInputReader

from nerdd_link.input import StructureJsonReader
from nerdd_link.storage import FileSystemStorage


@pytest.fixture
def storage(tmp_path) -> FileSystemStorage:
    storage = FileSystemStorage(str(tmp_path))
    for source_id in ("source-1", "source-2"):
        with storage.get_source_file_handle(source_id, "wb") as source_file:
            source_file.write(b"input")
    return storage


# an explore callable that will always return 5 dummy entries
def dummy_explore(_: Any) -> Iterator[MoleculeEntry]:
    for _ in range(5):
        yield MoleculeEntry("value", "test", ("raw_input",), None, [])


def invalid_explore(input: Any) -> Iterator[MoleculeEntry]:
    yield from InvalidInputReader().read(input, lambda _: iter(()))


def test_prepends_filename_to_every_source(storage: FileSystemStorage) -> None:
    input_stream = io.StringIO(json.dumps([{"id": "source-1", "filename": "input.smi"}]))

    entries = list(StructureJsonReader(storage).read(input_stream, dummy_explore))

    assert all(entry.source == ("input.smi",) for entry in entries)


def test_leaves_sources_unchanged_without_filename(storage: FileSystemStorage) -> None:
    contents = [{"id": "source-1", "filename": None}, {"id": "source-2"}]
    input_stream = io.StringIO(json.dumps(contents))

    entries = list(StructureJsonReader(storage).read(input_stream, dummy_explore))

    assert all(entry.source == ("raw_input",) for entry in entries)


def test_replaces_nested_non_text_invalid_input_with_filename(storage: FileSystemStorage) -> None:
    input_stream = io.StringIO(json.dumps([{"id": "source-1", "filename": "input.smi"}]))

    entries = list(StructureJsonReader(storage).read(input_stream, invalid_explore))

    assert entries[0].raw_input == "input.smi"


def test_replaces_nested_non_text_invalid_input_with_source_id_without_filename(
    storage: FileSystemStorage,
) -> None:
    input_stream = io.StringIO(json.dumps([{"id": "source-1"}]))

    entries = list(StructureJsonReader(storage).read(input_stream, invalid_explore))

    assert entries[0].raw_input == "source-1"

import pytest

from nerdd_link import FileSystemStorage


def test_repr():
    storage = FileSystemStorage("/path/to/data")

    assert repr(storage) == "FileSystemStorage('/path/to/data')"


def test_validation_creates_missing_root(tmp_path):
    root_path = tmp_path / "missing"
    storage = FileSystemStorage(str(root_path))

    storage.validate()

    assert root_path.is_dir()


def test_validation_rejects_file_root(tmp_path):
    root_path = tmp_path / "root-file"
    root_path.touch()
    storage = FileSystemStorage(str(root_path))

    with pytest.raises(ValueError, match="not a directory"):
        storage.validate()


def test_get_file_size(tmp_path):
    storage = FileSystemStorage(str(tmp_path))
    file_path = storage.get_source_file_path("source-1")

    with storage.get_file_handle(file_path, "wb") as handle:
        handle.write(b"content")

    assert storage.get_file_size(file_path) == len(b"content")

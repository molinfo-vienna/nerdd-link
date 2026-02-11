import io

import pytest

from nerdd_link import FileSystemStorage, MirroredStorage


class _FailingWriteStorage(FileSystemStorage):
    def _get_binary_file_handle(self, identifier, mode):
        if mode == "wb":
            return _FailingWriter()
        return super()._get_binary_file_handle(identifier, mode)


class _FailingWriter(io.BytesIO):
    def write(self, buffer):
        raise OSError("write failed")


class _FailingDeleteStorage(FileSystemStorage):
    def _delete_file(self, identifier):
        raise OSError("delete failed")


def test_repr():
    first = FileSystemStorage("/path/1")
    second = FileSystemStorage("/path/2")

    storage = MirroredStorage(first, second)

    assert repr(storage) == (
        "MirroredStorage(FileSystemStorage('/path/1'), FileSystemStorage('/path/2'))"
    )


def test_requires_at_least_one_storage():
    with pytest.raises(ValueError, match="at least one storage"):
        MirroredStorage()


def test_writes_binary_files_to_every_storage(tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    storage = MirroredStorage(first, second)

    with storage.get_source_file_handle("source-1", "wb") as handle:
        handle.write(b"content")

    for backend in (first, second):
        with backend.get_source_file_handle("source-1", "rb") as handle:
            assert handle.read() == b"content"


def test_writes_text_files_to_every_storage(tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    storage = MirroredStorage(first, second)

    with storage.get_output_file_handle("job-1", "txt", "w") as handle:
        handle.write("content")

    for backend in (first, second):
        with backend.get_output_file_handle("job-1", "txt", "r") as handle:
            assert handle.read() == "content"


def test_reads_from_first_storage_containing_the_file(tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    storage = MirroredStorage(first, second)

    with second.get_source_file_handle("source-1", "wb") as handle:
        handle.write(b"second")

    with storage.get_source_file_handle("source-1", "rb") as handle:
        assert handle.read() == b"second"

    with first.get_source_file_handle("source-1", "wb") as handle:
        handle.write(b"first")

    with storage.get_source_file_handle("source-1", "rb") as handle:
        assert handle.read() == b"first"


def test_get_file_size_uses_first_storage_containing_file(tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    storage = MirroredStorage(first, second)
    file_path = storage.get_source_file_path("source-1")

    for backend, content in ((first, b"first"), (second, b"second-content")):
        with backend.get_file_handle(file_path, "wb") as handle:
            handle.write(content)

    assert storage.get_file_size(file_path) == len(b"first")


def test_merges_directory_listings_without_duplicates(tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    storage = MirroredStorage(first, second)

    for backend, checkpoint_ids in ((first, (1, 2)), (second, (2, 3))):
        for checkpoint_id in checkpoint_ids:
            with backend.get_checkpoint_file_handle("job-1", checkpoint_id, "wb"):
                pass

    assert storage.checkpoint_file_exists("job-1", 3)
    assert list(storage.iter_checkpoint_file_paths("job-1")) == [
        (1, "file://jobs/job-1/inputs/checkpoint_1.pickle"),
        (2, "file://jobs/job-1/inputs/checkpoint_2.pickle"),
        (3, "file://jobs/job-1/inputs/checkpoint_3.pickle"),
    ]


def test_attempts_write_on_every_storage_before_raising(tmp_path):
    failing = _FailingWriteStorage(str(tmp_path / "failing"))
    healthy = FileSystemStorage(str(tmp_path / "healthy"))
    storage = MirroredStorage(failing, healthy)

    handle = storage.get_source_file_handle("source-1", "wb")
    with pytest.raises(OSError, match="write failed"):
        handle.write(b"content")
    handle.close()

    with healthy.get_source_file_handle("source-1", "rb") as healthy_handle:
        assert healthy_handle.read() == b"content"


def test_attempts_delete_on_every_storage_before_raising(tmp_path):
    failing = _FailingDeleteStorage(str(tmp_path / "failing"))
    healthy = FileSystemStorage(str(tmp_path / "healthy"))
    storage = MirroredStorage(failing, healthy)

    with healthy.get_source_file_handle("source-1", "wb"):
        pass

    with pytest.raises(OSError, match="delete failed"):
        storage.delete_source_file("source-1")

    assert not healthy.source_file_exists("source-1")


def test_validation_validates_every_child(mocker, tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    first_validate = mocker.spy(first, "validate")
    second_validate = mocker.spy(second, "validate")

    MirroredStorage(first, second).validate()

    first_validate.assert_called_once_with()
    second_validate.assert_called_once_with()

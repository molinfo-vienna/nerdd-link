from nerdd_link import ChainedStorage, FileSystemStorage
from nerdd_link.storage import PropertyFilePathSpec


def test_repr():
    first = FileSystemStorage("/path/1")
    second = FileSystemStorage("/path/2")

    storage = ChainedStorage(first, second)

    assert repr(storage) == (
        "ChainedStorage(FileSystemStorage('/path/1'), FileSystemStorage('/path/2'))"
    )


def test_validation_validates_every_child(mocker, tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    first_validate = mocker.spy(first, "validate")
    second_validate = mocker.spy(second, "validate")

    ChainedStorage(first, second).validate()

    first_validate.assert_called_once_with()
    second_validate.assert_called_once_with()


def test_get_file_size_uses_first_storage_containing_file(tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    storage = ChainedStorage(first, second)
    file_path = storage.get_source_file_path("source-1")

    for backend, content in ((first, b"first"), (second, b"second-content")):
        with backend.get_file_handle(file_path, "wb") as handle:
            handle.write(content)

    assert storage.get_file_size(file_path) == len(b"first")


def test_parse_property_file_path_uses_matching_child_prefix(tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    first._prefix = "first"
    second = FileSystemStorage(str(tmp_path / "second"))
    second._prefix = "second"

    storage = ChainedStorage(first, second)

    assert storage.parse_property_file_path(
        "second://jobs/123/results/preprocessed_mol/0"
    ) == PropertyFilePathSpec(
        job_id="123",
        property_name="preprocessed_mol",
        record_id="0",
    )

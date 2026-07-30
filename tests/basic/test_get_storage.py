import pytest
import rich_click as click

from nerdd_link import ChainedStorage, FileSystemStorage, MirroredStorage, S3Storage
from nerdd_link.cli.get_storage import get_storage

S3_OPTIONS = ("http://s3.example.com", "bucket", "access-key", "secret-key")


def test_validates_before_returning(mocker, tmp_path):
    validate = mocker.patch.object(FileSystemStorage, "validate")

    get_storage(str(tmp_path), None, None, None, None)

    validate.assert_called_once_with()


def test_single_mode_uses_file_system_storage(tmp_path):
    storage = get_storage(str(tmp_path), None, None, None, None)

    assert isinstance(storage, FileSystemStorage)


def test_single_mode_uses_s3_storage(mocker):
    mocker.patch("nerdd_link.storage.s3_storage.boto3.client")

    storage = get_storage(None, *S3_OPTIONS)

    assert isinstance(storage, S3Storage)


@pytest.mark.parametrize(
    ("mode", "storage_class"),
    [("chained", ChainedStorage), ("mirrored", MirroredStorage)],
)
def test_combined_modes_combine_s3_and_file_system_storage(mocker, tmp_path, mode, storage_class):
    mocker.patch("nerdd_link.storage.s3_storage.boto3.client")

    storage = get_storage(str(tmp_path), *S3_OPTIONS, mode=mode)

    assert isinstance(storage, storage_class)
    assert isinstance(storage._storages[0], S3Storage)
    assert isinstance(storage._storages[1], FileSystemStorage)


def test_single_mode_rejects_multiple_storage_options(tmp_path):
    with pytest.raises(click.UsageError, match="accepts only one storage backend"):
        get_storage(str(tmp_path), *S3_OPTIONS)


def test_single_mode_rejects_partial_s3_options_with_data_directory(tmp_path):
    with pytest.raises(click.UsageError, match="subset of S3 options"):
        get_storage(str(tmp_path), "http://s3.example.com", None, None, None)


def test_rejects_missing_storage_options():
    with pytest.raises(click.UsageError, match="At least --data-dir or all S3 options"):
        get_storage(None, None, None, None, None)


def test_rejects_unknown_storage_mode(tmp_path):
    with pytest.raises(ValueError, match="Invalid storage mode"):
        get_storage(str(tmp_path), None, None, None, None, mode="unknown")  # type: ignore[arg-type]

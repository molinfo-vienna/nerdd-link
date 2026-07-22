import pytest

from nerdd_link.storage import (
    CheckpointFilePathSpec,
    ModuleFilePathSpec,
    OutputFilePathSpec,
    PropertyFilePathSpec,
    ResultCheckpointFilePathSpec,
    SourceFilePathSpec,
    Storage,
    WrongPrefixError,
)


class DummyStorage(Storage):
    def __init__(self) -> None:
        super().__init__("dummy")

    def _validate(self) -> None:
        raise NotImplementedError

    def _iter_directory(self, identifier):
        raise NotImplementedError

    def _file_exists(self, identifier):
        raise NotImplementedError

    def _get_file_size(self, identifier):
        raise NotImplementedError

    def _get_binary_file_handle(self, identifier, mode):
        raise NotImplementedError

    def _delete_file(self, identifier):
        raise NotImplementedError


def test_module_file_path_round_trip():
    storage = DummyStorage()

    file_path = storage.get_module_file_path("module-1")

    assert storage.parse_module_file_path(file_path) == ModuleFilePathSpec(module_id="module-1")


def test_source_file_path_round_trip():
    storage = DummyStorage()

    file_path = storage.get_source_file_path("source-1")

    assert storage.parse_source_file_path(file_path) == SourceFilePathSpec(source_id="source-1")


def test_checkpoint_file_path_round_trip():
    storage = DummyStorage()

    file_path = storage.get_checkpoint_file_path("job-1", 2)

    assert storage.parse_checkpoint_file_path(file_path) == CheckpointFilePathSpec(
        job_id="job-1", checkpoint_id=2
    )


def test_result_checkpoint_file_path_round_trip():
    storage = DummyStorage()

    file_path = storage.get_result_checkpoint_file_path("job-1", 2)

    assert storage.parse_result_checkpoint_file_path(file_path) == ResultCheckpointFilePathSpec(
        job_id="job-1", checkpoint_id=2
    )


def test_property_file_path_round_trip():
    storage = DummyStorage()

    file_path = storage.get_property_file_path("job-1", "logp", "record-1")

    assert storage.parse_property_file_path(file_path) == PropertyFilePathSpec(
        job_id="job-1", property_name="logp", record_id="record-1"
    )


def test_output_file_path_round_trip():
    storage = DummyStorage()

    file_path = storage.get_output_file_path("job-1", "sdf.gz")

    assert storage.parse_output_file_path(file_path) == OutputFilePathSpec(
        job_id="job-1", output_format="sdf.gz"
    )


def test_get_file_size_rejects_wrong_prefix():
    storage = DummyStorage()

    with pytest.raises(WrongPrefixError):
        storage.get_file_size("file://sources/source-1")

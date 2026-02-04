from nerdd_link import (
    CheckpointFilePathSpec,
    FileSystemStorage,
    ModuleFilePathSpec,
    OutputFilePathSpec,
    PropertyFilePathSpec,
    ResultsFilePathSpec,
    SourceFilePathSpec,
)


def test_module_file_path_round_trip(tmp_path):
    storage = FileSystemStorage(str(tmp_path))

    file_path = storage.get_module_file_path("module-1")

    assert storage.parse_module_file_path(file_path) == ModuleFilePathSpec(module_id="module-1")


def test_source_file_path_round_trip(tmp_path):
    storage = FileSystemStorage(str(tmp_path))

    file_path = storage.get_source_file_path("source-1")

    assert storage.parse_source_file_path(file_path) == SourceFilePathSpec(source_id="source-1")


def test_checkpoint_file_path_round_trip(tmp_path):
    storage = FileSystemStorage(str(tmp_path))

    file_path = storage.get_checkpoint_file_path("job-1", 2)

    assert storage.parse_checkpoint_file_path(file_path) == CheckpointFilePathSpec(
        job_id="job-1", checkpoint_id=2
    )


def test_results_file_path_round_trip(tmp_path):
    storage = FileSystemStorage(str(tmp_path))

    file_path = storage.get_results_file_path("job-1", 2)

    assert storage.parse_results_file_path(file_path) == ResultsFilePathSpec(
        job_id="job-1", checkpoint_id=2
    )


def test_property_file_path_round_trip(tmp_path):
    storage = FileSystemStorage(str(tmp_path))

    file_path = storage.get_property_file_path("job-1", "logp", "record-1")

    assert storage.parse_property_file_path(file_path) == PropertyFilePathSpec(
        job_id="job-1", property_name="logp", record_id="record-1"
    )


def test_output_file_path_round_trip(tmp_path):
    storage = FileSystemStorage(str(tmp_path))

    file_path = storage.get_output_file_path("job-1", "sdf.gz")

    assert storage.parse_output_file_path(file_path) == OutputFilePathSpec(
        job_id="job-1", output_format="sdf.gz"
    )

import io
import posixpath
from abc import ABC, abstractmethod
from typing import IO, BinaryIO, Iterator, Literal, NamedTuple, Tuple

from .wrong_prefix_error import WrongPrefixError

__all__ = [
    "CheckpointFilePathSpec",
    "ModuleFilePathSpec",
    "OutputFilePathSpec",
    "PropertyFilePathSpec",
    "ResultCheckpointFilePathSpec",
    "SourceFilePathSpec",
    "Storage",
]


class ModuleFilePathSpec(NamedTuple):
    module_id: str


class SourceFilePathSpec(NamedTuple):
    source_id: str


class CheckpointFilePathSpec(NamedTuple):
    job_id: str
    checkpoint_id: int


class ResultCheckpointFilePathSpec(NamedTuple):
    job_id: str
    checkpoint_id: int


class PropertyFilePathSpec(NamedTuple):
    job_id: str
    property_name: str
    record_id: str


class OutputFilePathSpec(NamedTuple):
    job_id: str
    output_format: str


class Storage(ABC):
    """Interface for the persistent data used while processing NERDD jobs."""

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    #
    # Abstract methods
    #
    @abstractmethod
    def _validate(self) -> None: ...

    @abstractmethod
    def _iter_directory(self, identifier: str) -> Iterator[str]: ...

    @abstractmethod
    def _file_exists(self, identifier: str) -> bool: ...

    @abstractmethod
    def _get_file_size(self, identifier: str) -> int: ...

    @abstractmethod
    def _get_binary_file_handle(self, identifier: str, mode: Literal["rb", "wb"]) -> BinaryIO: ...

    @abstractmethod
    def _delete_file(self, identifier: str) -> None: ...

    #
    # Validation
    #
    def validate(self) -> None:
        """Verify that this storage backend is ready to be used."""
        self._validate()

    #
    # Modules
    #
    def _get_module_file_path(self, module_id: str) -> str:
        return posixpath.join("modules", module_id)

    def get_module_file_path(self, module_id: str) -> str:
        return self._prefix_file_path(self._get_module_file_path(module_id))

    def parse_module_file_path(self, file_path: str) -> ModuleFilePathSpec:
        parts = self._parse_file_path_parts(file_path, "module", 2)
        if parts[0] != "modules":
            raise self._invalid_file_path("module", file_path)
        return ModuleFilePathSpec(module_id=parts[1])

    def get_module_file_handle(self, module_id: str, mode: str) -> IO:
        return self._get_file_handle(self._get_module_file_path(module_id), mode)

    def module_file_exists(self, module_id: str) -> bool:
        return self._file_exists(self._get_module_file_path(module_id))

    #
    # Sources
    #
    def _get_source_file_path(self, source_id: str) -> str:
        return posixpath.join("sources", source_id)

    def get_source_file_path(self, source_id: str) -> str:
        return self._prefix_file_path(self._get_source_file_path(source_id))

    def parse_source_file_path(self, file_path: str) -> SourceFilePathSpec:
        parts = self._parse_file_path_parts(file_path, "source", 2)
        if parts[0] != "sources":
            raise self._invalid_file_path("source", file_path)
        return SourceFilePathSpec(source_id=parts[1])

    def get_source_file_handle(self, source_id: str, mode: str) -> IO:
        return self._get_file_handle(self._get_source_file_path(source_id), mode)

    def source_file_exists(self, source_id: str) -> bool:
        return self._file_exists(self._get_source_file_path(source_id))

    def delete_source_file(self, source_id: str) -> None:
        self._delete_file(self._get_source_file_path(source_id))

    #
    # Checkpoints
    #
    def _get_checkpoint_directory_path(self, job_id: str) -> str:
        return posixpath.join("jobs", job_id, "inputs")

    def _get_checkpoint_file_path(self, job_id: str, checkpoint_id: int) -> str:
        return posixpath.join(
            self._get_checkpoint_directory_path(job_id), f"checkpoint_{checkpoint_id}.pickle"
        )

    def get_checkpoint_file_path(self, job_id: str, checkpoint_id: int) -> str:
        return self._prefix_file_path(self._get_checkpoint_file_path(job_id, checkpoint_id))

    def parse_checkpoint_file_path(self, file_path: str) -> CheckpointFilePathSpec:
        parts = self._parse_file_path_parts(file_path, "checkpoint", 4)
        if parts[0] != "jobs" or parts[2] != "inputs":
            raise self._invalid_file_path("checkpoint", file_path)
        checkpoint_id = self._parse_checkpoint_id(parts[3], "checkpoint", file_path)
        return CheckpointFilePathSpec(job_id=parts[1], checkpoint_id=checkpoint_id)

    def get_checkpoint_file_handle(self, job_id: str, checkpoint_id: int, mode: str) -> IO:
        return self._get_file_handle(self._get_checkpoint_file_path(job_id, checkpoint_id), mode)

    def checkpoint_file_exists(self, job_id: str, checkpoint_id: int) -> bool:
        return self._file_exists(self._get_checkpoint_file_path(job_id, checkpoint_id))

    def delete_checkpoint_file(self, job_id: str, checkpoint_id: int) -> None:
        self._delete_file(self._get_checkpoint_file_path(job_id, checkpoint_id))

    def iter_checkpoint_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
        directory = self._get_checkpoint_directory_path(job_id)
        for checkpoint_id, identifier in self._iter_checkpoint_files(directory):
            yield checkpoint_id, self._prefix_file_path(identifier)

    #
    # Result checkpoints
    #
    def _get_results_directory_path(self, job_id: str) -> str:
        return posixpath.join("jobs", job_id, "results")

    def _get_result_checkpoint_file_path(self, job_id: str, checkpoint_id: int) -> str:
        return posixpath.join(
            self._get_results_directory_path(job_id), f"checkpoint_{checkpoint_id}.pickle"
        )

    def get_result_checkpoint_file_path(self, job_id: str, checkpoint_id: int) -> str:
        return self._prefix_file_path(self._get_result_checkpoint_file_path(job_id, checkpoint_id))

    def parse_result_checkpoint_file_path(self, file_path: str) -> ResultCheckpointFilePathSpec:
        parts = self._parse_file_path_parts(file_path, "result checkpoint", 4)
        if parts[0] != "jobs" or parts[2] != "results":
            raise self._invalid_file_path("result checkpoint", file_path)
        checkpoint_id = self._parse_checkpoint_id(parts[3], "result checkpoint", file_path)
        return ResultCheckpointFilePathSpec(job_id=parts[1], checkpoint_id=checkpoint_id)

    def get_result_checkpoint_file_handle(self, job_id: str, checkpoint_id: int, mode: str) -> IO:
        return self._get_file_handle(
            self._get_result_checkpoint_file_path(job_id, checkpoint_id), mode
        )

    def result_checkpoint_file_exists(self, job_id: str, checkpoint_id: int) -> bool:
        return self._file_exists(self._get_result_checkpoint_file_path(job_id, checkpoint_id))

    def delete_result_checkpoint_file(self, job_id: str, checkpoint_id: int) -> None:
        self._delete_file(self._get_result_checkpoint_file_path(job_id, checkpoint_id))

    def iter_result_checkpoint_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
        directory = self._get_results_directory_path(job_id)
        for checkpoint_id, identifier in self._iter_checkpoint_files(directory):
            yield checkpoint_id, self._prefix_file_path(identifier)

    #
    # Properties
    #
    def _get_property_file_path(self, job_id: str, property_name: str, record_id: str) -> str:
        return posixpath.join("jobs", job_id, "results", property_name, record_id)

    def get_property_file_path(self, job_id: str, property_name: str, record_id: str) -> str:
        return self._prefix_file_path(
            self._get_property_file_path(job_id, property_name, record_id)
        )

    def parse_property_file_path(self, file_path: str) -> PropertyFilePathSpec:
        parts = self._parse_file_path_parts(file_path, "property", 5)
        if parts[0] != "jobs" or parts[2] != "results":
            raise self._invalid_file_path("property", file_path)
        return PropertyFilePathSpec(
            job_id=parts[1],
            property_name=parts[3],
            record_id=parts[4],
        )

    def get_property_file_handle(
        self, job_id: str, property_name: str, record_id: str, mode: str
    ) -> IO:
        identifier = self._get_property_file_path(job_id, property_name, record_id)
        return self._get_file_handle(identifier, mode)

    #
    # Output
    #
    def _get_output_file_path(self, job_id: str, output_format: str) -> str:
        return posixpath.join("jobs", job_id, "outputs", f"result.{output_format}")

    def get_output_file_path(self, job_id: str, output_format: str) -> str:
        return self._prefix_file_path(self._get_output_file_path(job_id, output_format))

    def parse_output_file_path(self, file_path: str) -> OutputFilePathSpec:
        parts = self._parse_file_path_parts(file_path, "output", 4)
        filename = parts[3]
        if parts[0] != "jobs" or parts[2] != "outputs" or not filename.startswith("result."):
            raise self._invalid_file_path("output", file_path)

        output_format = filename[len("result.") :]
        if not self._is_valid_file_path_component(output_format):
            raise self._invalid_file_path("output", file_path)
        return OutputFilePathSpec(job_id=parts[1], output_format=output_format)

    def get_output_file_handle(self, job_id: str, output_format: str, mode: str) -> IO:
        return self._get_file_handle(self._get_output_file_path(job_id, output_format), mode)

    def output_file_exists(self, job_id: str, output_format: str) -> bool:
        return self._file_exists(self._get_output_file_path(job_id, output_format))

    def delete_output_file(self, job_id: str, output_format: str) -> None:
        self._delete_file(self._get_output_file_path(job_id, output_format))

    #
    # Files
    #
    def get_file_handle(self, file_path: str, mode: str) -> IO:
        return self._get_file_handle(self._unprefix_file_path(file_path), mode)

    def file_exists(self, file_path: str) -> bool:
        return self._file_exists(self._unprefix_file_path(file_path))

    def get_file_size(self, file_path: str) -> int:
        """Return the size of a file in bytes."""
        return self._get_file_size(self._unprefix_file_path(file_path))

    def delete_file(self, file_path: str) -> None:
        self._delete_file(self._unprefix_file_path(file_path))

    #
    # Helpers
    #
    def _get_file_handle(self, identifier: str, mode: str) -> IO:
        if mode == "rb":
            return self._get_binary_file_handle(identifier, "rb")
        elif mode == "wb":
            return self._get_binary_file_handle(identifier, "wb")
        elif mode == "r":
            return io.TextIOWrapper(
                self._get_binary_file_handle(identifier, "rb"), encoding="utf-8"
            )
        elif mode == "w":
            return io.TextIOWrapper(
                self._get_binary_file_handle(identifier, "wb"), encoding="utf-8"
            )
        else:
            raise ValueError(
                "Storage only supports read and write modes ('r', 'w', 'rb', and 'wb')."
            )

    def _prefix_file_path(self, path: str) -> str:
        return f"{self._prefix}://{path}"

    def _unprefix_file_path(self, file_path: str) -> str:
        prefix = f"{self._prefix}://"

        # For backwards compatibility, we associate the paths
        # * file:///data/ with file:// (and ignore the /data/ prefix)
        # * /data/ with file:// (and ignore the /data/ prefix)
        # Otherwise, we expect the file_path to start with the prefix.
        # TODO: delete this legacy behaviour once the whole system is migrated to S3 storage
        if self._prefix == "file" and file_path.startswith("file:///data/"):
            return file_path[len("file:///data/") :]
        elif file_path.startswith(prefix):
            return file_path[len(prefix) :]
        elif self._prefix == "file" and file_path.startswith("/data/"):
            return file_path[len("/data/") :]
        else:
            raise WrongPrefixError(self._prefix, file_path)

    def _parse_file_path_parts(
        self, file_path: str, file_type: str, expected_num_parts: int
    ) -> Tuple[str, ...]:
        identifier = self._unprefix_file_path(file_path)
        parts = tuple(identifier.split("/"))
        if len(parts) != expected_num_parts or any(
            not self._is_valid_file_path_component(part) for part in parts
        ):
            raise self._invalid_file_path(file_type, file_path)
        return parts

    def _parse_checkpoint_id(self, filename: str, file_type: str, file_path: str) -> int:
        prefix = "checkpoint_"
        suffix = ".pickle"
        if not filename.startswith(prefix) or not filename.endswith(suffix):
            raise self._invalid_file_path(file_type, file_path)

        checkpoint_id = filename[len(prefix) : -len(suffix)]
        if not checkpoint_id.isascii() or not checkpoint_id.isdecimal():
            raise self._invalid_file_path(file_type, file_path)
        return int(checkpoint_id)

    def _is_valid_file_path_component(self, component: str) -> bool:
        return component not in {"", ".", ".."} and "\\" not in component

    def _invalid_file_path(self, file_type: str, file_path: str) -> ValueError:
        return ValueError(f"Invalid {file_type} file path: {file_path}")

    def _iter_checkpoint_files(self, directory: str) -> Iterator[Tuple[int, str]]:
        checkpoint_files = []
        for identifier in self._iter_directory(directory):
            filename = posixpath.basename(identifier)
            if filename.startswith("checkpoint_") and filename.endswith(".pickle"):
                checkpoint_id = int(filename[len("checkpoint_") : -len(".pickle")])
                checkpoint_files.append((checkpoint_id, identifier))

        yield from sorted(checkpoint_files, key=lambda item: item[0])

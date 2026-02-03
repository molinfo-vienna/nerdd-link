import io
import posixpath
from abc import ABC, abstractmethod
from typing import IO, BinaryIO, Iterator, Literal, Tuple, Union

from .wrong_prefix_error import WrongPrefixError

__all__ = ["Storage"]


class Storage(ABC):
    """Interface for the persistent data used while processing NERDD jobs."""

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    #
    # Modules
    #
    def _get_module_file_path(self, module_id: str) -> str:
        return posixpath.join("modules", module_id)

    def get_module_file_path(self, module_id: str) -> str:
        return self._prefix_file_path(self._get_module_file_path(module_id))

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

    def _get_checkpoint_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return posixpath.join(
            self._get_checkpoint_directory_path(job_id), f"checkpoint_{checkpoint_id}.pickle"
        )

    def get_checkpoint_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return self._prefix_file_path(self._get_checkpoint_file_path(job_id, checkpoint_id))

    def get_checkpoint_file_handle(
        self, job_id: str, checkpoint_id: Union[int, str], mode: str
    ) -> IO:
        return self._get_file_handle(self._get_checkpoint_file_path(job_id, checkpoint_id), mode)

    def checkpoint_file_exists(self, job_id: str, checkpoint_id: Union[int, str]) -> bool:
        return self._file_exists(self._get_checkpoint_file_path(job_id, checkpoint_id))

    def delete_checkpoint_file(self, job_id: str, checkpoint_id: Union[int, str]) -> None:
        self._delete_file(self._get_checkpoint_file_path(job_id, checkpoint_id))

    def iter_checkpoint_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
        directory = self._get_checkpoint_directory_path(job_id)
        for checkpoint_id, identifier in self._iter_checkpoint_files(directory):
            yield checkpoint_id, self._prefix_file_path(identifier)

    #
    # Results
    #
    def _get_results_directory_path(self, job_id: str) -> str:
        return posixpath.join("jobs", job_id, "results")

    def _get_results_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return posixpath.join(
            self._get_results_directory_path(job_id), f"checkpoint_{checkpoint_id}.pickle"
        )

    def get_results_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return self._prefix_file_path(self._get_results_file_path(job_id, checkpoint_id))

    def get_results_file_handle(self, job_id: str, checkpoint_id: Union[int, str], mode: str) -> IO:
        return self._get_file_handle(self._get_results_file_path(job_id, checkpoint_id), mode)

    def results_file_exists(self, job_id: str, checkpoint_id: Union[int, str]) -> bool:
        return self._file_exists(self._get_results_file_path(job_id, checkpoint_id))

    def delete_results_file(self, job_id: str, checkpoint_id: Union[int, str]) -> None:
        self._delete_file(self._get_results_file_path(job_id, checkpoint_id))

    def iter_results_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
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

    def delete_file(self, file_path: str) -> None:
        self._delete_file(self._unprefix_file_path(file_path))

    #
    # Abstract methods
    #
    @abstractmethod
    def _iter_directory(self, identifier: str) -> Iterator[str]: ...

    @abstractmethod
    def _file_exists(self, identifier: str) -> bool: ...

    @abstractmethod
    def _get_binary_file_handle(self, identifier: str, mode: Literal["rb", "wb"]) -> BinaryIO: ...

    @abstractmethod
    def _delete_file(self, identifier: str) -> None: ...

    #
    # Helpers
    #
    def _get_file_handle(self, identifier: str, mode: str) -> IO:
        if mode == "rb":
            return self._get_binary_file_handle(identifier, "rb")
        if mode == "wb":
            return self._get_binary_file_handle(identifier, "wb")
        if mode == "r":
            return io.TextIOWrapper(
                self._get_binary_file_handle(identifier, "rb"), encoding="utf-8"
            )
        if mode == "w":
            return io.TextIOWrapper(
                self._get_binary_file_handle(identifier, "wb"), encoding="utf-8"
            )
        raise ValueError("Storage only supports read and write modes ('r', 'w', 'rb', and 'wb').")

    def _prefix_file_path(self, path: str) -> str:
        return f"{self._prefix}://{path}"

    def _unprefix_file_path(self, file_path: str) -> str:
        prefix = f"{self._prefix}://"
        if not file_path.startswith(prefix):
            raise WrongPrefixError(self._prefix, file_path)
        return file_path[len(prefix) :]

    def _iter_checkpoint_files(self, directory: str) -> Iterator[Tuple[int, str]]:
        checkpoint_files = []
        for identifier in self._iter_directory(directory):
            filename = posixpath.basename(identifier)
            if filename.startswith("checkpoint_") and filename.endswith(".pickle"):
                checkpoint_id = int(filename[len("checkpoint_") : -len(".pickle")])
                checkpoint_files.append((checkpoint_id, identifier))

        yield from sorted(checkpoint_files, key=lambda item: item[0])

import posixpath
from abc import ABC, abstractmethod
from typing import IO, Iterator, Tuple, Union

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
    def _get_checkpoint_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return posixpath.join("jobs", job_id, "inputs", f"checkpoint_{checkpoint_id}.pickle")

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

    @abstractmethod
    def _iter_checkpoint_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]: ...

    def iter_checkpoint_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
        for checkpoint_id, path in self._iter_checkpoint_file_paths(job_id):
            yield checkpoint_id, self._prefix_file_path(path)

    #
    # Results
    #
    def _get_results_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return posixpath.join("jobs", job_id, "results", f"checkpoint_{checkpoint_id}.pickle")

    def get_results_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return self._prefix_file_path(self._get_results_file_path(job_id, checkpoint_id))

    def get_results_file_handle(self, job_id: str, checkpoint_id: Union[int, str], mode: str) -> IO:
        return self._get_file_handle(self._get_results_file_path(job_id, checkpoint_id), mode)

    def results_file_exists(self, job_id: str, checkpoint_id: Union[int, str]) -> bool:
        return self._file_exists(self._get_results_file_path(job_id, checkpoint_id))

    def delete_results_file(self, job_id: str, checkpoint_id: Union[int, str]) -> None:
        self._delete_file(self._get_results_file_path(job_id, checkpoint_id))

    @abstractmethod
    def _iter_results_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]: ...

    def iter_results_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
        for checkpoint_id, path in self._iter_results_file_paths(job_id):
            yield checkpoint_id, self._prefix_file_path(path)

    def iter_results_file_handles(self, job_id: str, mode: str = "rb") -> Iterator[IO]:
        for _, identifier in self._iter_results_file_paths(job_id):
            yield self._get_file_handle(identifier, mode)

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
    # Helpers
    #
    @abstractmethod
    def _resolve_file_path(self, identifier: str) -> str: ...

    @abstractmethod
    def _file_exists(self, identifier: str) -> bool: ...

    @abstractmethod
    def _get_file_handle(self, identifier: str, mode: str) -> IO: ...

    @abstractmethod
    def _delete_file(self, identifier: str) -> None: ...

    def _prefix_file_path(self, path: str) -> str:
        return f"{self._prefix}://{path}"

    def _get_checkpoint_file_pattern(self, job_id: str) -> str:
        return posixpath.join("jobs", job_id, "inputs", "checkpoint_*.pickle")

    def _get_checkpoint_file_prefix(self, job_id: str) -> str:
        return posixpath.join("jobs", job_id, "inputs", "checkpoint_")

    def _get_results_file_pattern(self, job_id: str) -> str:
        return posixpath.join("jobs", job_id, "results", "checkpoint_*.pickle")

    def _get_results_file_prefix(self, job_id: str) -> str:
        return posixpath.join("jobs", job_id, "results", "checkpoint_")

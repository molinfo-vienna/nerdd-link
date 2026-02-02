from abc import ABC, abstractmethod
from typing import IO, Iterator, Tuple, Union

__all__ = ["Storage"]


class Storage(ABC):
    """Interface for the persistent data used while processing NERDD jobs."""

    @abstractmethod
    def get_module_file_path(self, module_id: str) -> str: ...

    @abstractmethod
    def get_module_file_handle(self, module_id: str, mode: str) -> IO: ...

    @abstractmethod
    def module_file_exists(self, module_id: str) -> bool: ...

    @abstractmethod
    def get_source_file_path(self, source_id: str) -> str: ...

    @abstractmethod
    def get_source_file_handle(self, source_id: str, mode: str) -> IO: ...

    @abstractmethod
    def source_file_exists(self, source_id: str) -> bool: ...

    @abstractmethod
    def delete_source_file(self, source_id: str) -> None: ...

    @abstractmethod
    def get_checkpoint_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str: ...

    @abstractmethod
    def get_results_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str: ...

    @abstractmethod
    def get_checkpoint_file_handle(
        self, job_id: str, checkpoint_id: Union[int, str], mode: str
    ) -> IO: ...

    @abstractmethod
    def checkpoint_file_exists(self, job_id: str, checkpoint_id: Union[int, str]) -> bool: ...

    @abstractmethod
    def delete_checkpoint_file(self, job_id: str, checkpoint_id: Union[int, str]) -> None: ...

    @abstractmethod
    def get_results_file_handle(
        self, job_id: str, checkpoint_id: Union[int, str], mode: str
    ) -> IO: ...

    @abstractmethod
    def results_file_exists(self, job_id: str, checkpoint_id: Union[int, str]) -> bool: ...

    @abstractmethod
    def delete_results_file(self, job_id: str, checkpoint_id: Union[int, str]) -> None: ...

    @abstractmethod
    def get_property_file_path(self, job_id: str, property_name: str, record_id: str) -> str: ...

    @abstractmethod
    def get_output_file(self, job_id: str, output_format: str) -> str: ...

    @abstractmethod
    def output_file_exists(self, job_id: str, output_format: str) -> bool: ...

    @abstractmethod
    def delete_output_file(self, job_id: str, output_format: str) -> None: ...

    @abstractmethod
    def iter_checkpoint_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]: ...

    @abstractmethod
    def iter_results_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]: ...

    @abstractmethod
    def iter_results_file_handles(self, job_id: str, mode: str = "rb") -> Iterator[IO]: ...

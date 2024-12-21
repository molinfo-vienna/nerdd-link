import os
from typing import IO, Iterator, Union

__all__ = ["FileSystem"]


def _get_handle_and_create_dirs(file_path: str, mode: str) -> IO:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return open(file_path, mode)


class FileSystem:
    def __init__(self, root_path: str) -> None:
        self.root_path = root_path

    #
    # DIRECTORIES
    #
    def get_sources_dir(self) -> str:
        result = os.path.join(self.root_path, "sources")
        os.makedirs(result, exist_ok=True)
        return result

    def get_jobs_dir(self) -> str:
        result = os.path.join(self.root_path, "jobs")
        os.makedirs(result, exist_ok=True)
        return result

    def get_job_dir(self, job_id: str) -> str:
        result = os.path.join(self.get_jobs_dir(), job_id)
        os.makedirs(result, exist_ok=True)
        return result

    def get_input_dir(self, job_id: str) -> str:
        result = os.path.join(self.get_job_dir(job_id), "inputs")
        os.makedirs(result, exist_ok=True)
        return result

    def get_results_dir(self, job_id: str) -> str:
        result = os.path.join(self.get_job_dir(job_id), "results")
        os.makedirs(result, exist_ok=True)
        return result

    def get_output_dir(self, job_id: str) -> str:
        result = os.path.join(self.get_job_dir(job_id), "outputs")
        os.makedirs(result, exist_ok=True)
        return result

    #
    # FILES
    #
    def get_source_file_path(self, source_id: str) -> str:
        return os.path.join(self.get_sources_dir(), source_id)

    def get_checkpoint_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return os.path.join(self.get_input_dir(job_id), f"checkpoint_{checkpoint_id}.pickle")

    def get_results_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return os.path.join(self.get_results_dir(job_id), f"checkpoint_{checkpoint_id}.pickle")

    def get_checkpoint_file_handle(
        self, job_id: str, checkpoint_id: Union[int, str], mode: str
    ) -> IO:
        return _get_handle_and_create_dirs(
            self.get_checkpoint_file_path(job_id, checkpoint_id), mode
        )

    def get_results_file_handle(self, job_id: str, checkpoint_id: Union[int, str], mode: str) -> IO:
        return _get_handle_and_create_dirs(self.get_results_file_path(job_id, checkpoint_id), mode)

    def get_output_file(self, job_id: str, output_format: str) -> str:
        return os.path.join(self.get_output_dir(job_id), f"result.{output_format}")

    def get_output_file_handle(self, job_id: str, output_format: str, mode: str) -> IO:
        return _get_handle_and_create_dirs(self.get_output_file(job_id, output_format), mode)

    def iter_results_file_handles(self, job_id: str, mode: str = "rb") -> Iterator[IO]:
        i = 0
        while os.path.exists(self.get_results_file_path(job_id, i)):
            yield self.get_results_file_handle(job_id, i, mode)
            i += 1

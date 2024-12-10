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
        return os.path.join(self.root_path, "sources")

    #
    # FILES
    #
    def get_checkpoint_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return os.path.join(
            self.root_path, f"jobs/{job_id}/input/checkpoint_{checkpoint_id}.pickle"
        )

    def get_results_file_path(self, job_id: str, checkpoint_id: Union[int, str]) -> str:
        return os.path.join(
            self.root_path, f"jobs/{job_id}/results/checkpoint_{checkpoint_id}.pickle"
        )

    def get_checkpoint_file_handle(
        self, job_id: str, checkpoint_id: Union[int, str], mode: str
    ) -> IO:
        return _get_handle_and_create_dirs(
            self.get_checkpoint_file_path(job_id, checkpoint_id), mode
        )

    def get_results_file_handle(self, job_id: str, checkpoint_id: Union[int, str], mode: str) -> IO:
        return _get_handle_and_create_dirs(self.get_results_file_path(job_id, checkpoint_id), mode)

    def iter_results_file_handles(self, job_id: str) -> Iterator[IO]:
        i = 0
        while os.path.exists(self.get_results_file_path(job_id, i)):
            yield self.get_results_file_handle(job_id, i, "rb")
            i += 1

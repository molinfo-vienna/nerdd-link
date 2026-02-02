import os
from glob import glob
from typing import IO, Iterator, Tuple

from .storage import Storage

__all__ = ["FileSystemStorage"]


class FileSystemStorage(Storage):
    def __init__(self, root_path: str) -> None:
        super().__init__("file")
        self.root_path = root_path

    #
    # Checkpoints
    #
    def _iter_checkpoint_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
        pattern = self._resolve_file_path(self._get_checkpoint_file_pattern(job_id))
        for path in glob(pattern):
            basename = os.path.basename(path)
            checkpoint_id = int(basename[len("checkpoint_") : -len(".pickle")])
            yield checkpoint_id, self._get_checkpoint_file_path(job_id, checkpoint_id)

    #
    # Results
    #
    def _iter_results_file_paths(self, job_id: str) -> Iterator[Tuple[int, str]]:
        pattern = self._resolve_file_path(self._get_results_file_pattern(job_id))
        for path in glob(pattern):
            basename = os.path.basename(path)
            checkpoint_id = int(basename[len("checkpoint_") : -len(".pickle")])
            yield checkpoint_id, self._get_results_file_path(job_id, checkpoint_id)

    #
    # Helpers
    #
    def _resolve_file_path(self, identifier: str) -> str:
        return os.path.join(self.root_path, *identifier.split("/"))

    def _file_exists(self, identifier: str) -> bool:
        return os.path.exists(self._resolve_file_path(identifier))

    def _get_file_handle(self, identifier: str, mode: str) -> IO:
        file_path = self._resolve_file_path(identifier)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return open(file_path, mode)

    def _delete_file(self, identifier: str) -> None:
        file_path = self._resolve_file_path(identifier)
        if os.path.exists(file_path):
            os.remove(file_path)

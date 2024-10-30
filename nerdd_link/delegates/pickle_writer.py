import pickle
from typing import IO, Any, Iterable

from nerdd_module.output import FileLike, FileWriter

__all__ = ["PickleWriter"]


class PickleWriter(FileWriter, output_format="pickle"):
    def __init__(self, output_file: FileLike) -> None:
        super().__init__(output_file, writes_bytes=True)

    def _write(self, output: IO[Any], entries: Iterable[dict]) -> None:
        results = list(entries)
        pickle.dump(results, output)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(output_file='{self._output_file}')"

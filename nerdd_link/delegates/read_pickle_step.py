import pickle
from typing import Iterator, Optional

from nerdd_module import Step

__all__ = ["ReadPickleStep"]


class ReadPickleStep(Step):
    def __init__(self, file_path: str):
        super().__init__(is_source=True)
        self.file_path = file_path

    def _run(self, source: Optional[Iterator[dict]] = None) -> Iterator[dict]:
        with open(self.file_path, "rb") as f:
            entries = pickle.load(f)

            yield from entries

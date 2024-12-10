import pickle
from io import IOBase
from typing import Iterable, Iterator, Optional, Union

from nerdd_module import Step

__all__ = ["ReadPickleStep"]


class ReadPickleStep(Step):
    def __init__(self, file_handles: Union[IOBase, Iterable[IOBase]]) -> None:
        super().__init__(is_source=True)
        if isinstance(file_handles, IOBase):
            file_handles = [file_handles]
        self.file_handles = file_handles

    def _run(self, source: Optional[Iterator[dict]] = None) -> Iterator[dict]:
        for file_handle in self.file_handles:
            with file_handle as f:
                entries = pickle.load(f)
                yield from entries

import pickle
from typing import IO, Any, Iterable, Iterator, Optional, Union

from nerdd_module.steps import Step

from ..polyfills import TypeGuard

__all__ = ["ReadPickleStep"]


def _is_file_handle(value: object) -> TypeGuard[IO[Any]]:
    return hasattr(value, "read")


class ReadPickleStep(Step):
    def __init__(self, file_handles: Union[IO, Iterable[IO]]) -> None:
        super().__init__(is_source=True)
        if _is_file_handle(file_handles):
            file_handles = [file_handles]
        self.file_handles = file_handles

    def _run(self, source: Optional[Iterator[dict]] = None) -> Iterator[dict]:
        for file_handle in self.file_handles:
            with file_handle as f:
                entries = pickle.load(f)
                yield from entries

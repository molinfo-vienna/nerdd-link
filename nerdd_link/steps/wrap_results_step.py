from typing import Iterator, Optional

from nerdd_module import Step

from ..types import ResultMessage

__all__ = ["WrapResultsStep"]


class WrapResultsStep(Step):
    def __init__(self) -> None:
        super().__init__()

    def _run(self, source: Optional[Iterator[dict]]) -> Iterator[dict]:
        assert source is not None, "Source iterator cannot be None."

        for record in source:
            yield {"topic": "results", "message": ResultMessage(**record)}

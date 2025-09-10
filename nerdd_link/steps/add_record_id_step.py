import logging
from typing import Iterator, Optional

from nerdd_module import Step

__all__ = ["AddRecordIdStep"]

logger = logging.getLogger(__name__)


class AddRecordIdStep(Step):
    def __init__(self, job_id: str) -> None:
        super().__init__()
        self._job_id = job_id

    def _run(self, source: Optional[Iterator[dict]]) -> Iterator[dict]:
        assert source is not None, "Source iterator cannot be None."

        job_id = self._job_id
        for record in source:
            # generate an id for the result
            mol_id = record["mol_id"]
            if "atom_id" in record:
                atom_id = record["atom_id"]
                id = f"{job_id}-{mol_id}-{atom_id}"
            elif "derivative_id" in record:
                derivative_id = record["derivative_id"]
                id = f"{job_id}-{mol_id}-{derivative_id}"
            else:
                id = f"{job_id}-{mol_id}"

            record["job_id"] = job_id
            record["id"] = id

            yield record

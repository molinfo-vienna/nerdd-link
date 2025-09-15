import logging
import pickle
from typing import Iterator, Optional

from nerdd_module import Step
from rdkit.Chem import Mol
from rdkit.Chem.PropertyMol import PropertyMol

from ..files import FileSystem
from ..types import CheckpointMessage, LogMessage
from ..utils import batched

__all__ = ["WriteCheckpointsStep"]

logger = logging.getLogger(__name__)


class WriteCheckpointsStep(Step):
    def __init__(
        self,
        filesystem: FileSystem,
        job_id: str,
        job_type: str,
        checkpoint_size: int,
        max_num_molecules: int,
        params: dict,
    ) -> None:
        super().__init__()
        self._file_system = filesystem
        self._job_id = job_id
        self._job_type = job_type
        self._checkpoint_size = checkpoint_size
        self._max_num_molecules = max_num_molecules
        self._params = params

    def _run(self, source: Optional[Iterator[dict]]) -> Iterator[dict]:
        assert source is not None, "Source iterator cannot be None."

        # iterate through the entries
        # create batches of size checkpoint_size
        # limit the number of molecules to max_num_molecules
        batches = batched(source, self._checkpoint_size)
        num_entries = 0
        num_checkpoints = 0
        for i, batch in enumerate(batches):
            # max_num_molecules might be reached within the batch
            num_store = min(len(batch), self._max_num_molecules - num_entries)

            # store batch in data_dir
            with self._file_system.get_checkpoint_file_handle(self._job_id, i, "wb") as f:
                results = list(batch[:num_store])

                # Convert Mol to PropertyMol to keep properties. Unfortunately, this code is
                # redundant with the code in mol_pickle_converter, but we need it here, because
                # converters are not applied in the short pipeline using this step.
                for result in results:
                    for k, v in result.items():
                        if isinstance(v, Mol):
                            result[k] = PropertyMol(v)

                pickle.dump(results, f)

            # send a tuple to checkpoints topic
            yield {
                "topic": f"{self._job_type}-checkpoints",
                "message": CheckpointMessage(
                    job_id=self._job_id,
                    checkpoint_id=i,
                    params=self._params,
                ),
            }

            num_entries += num_store
            num_checkpoints += 1

            if num_entries >= self._max_num_molecules:
                break

        logger.info(
            f"Wrote {i + 1} checkpoints containing {num_entries} entries for job {self._job_id}"
        )

        # figure out whether this job has more molecules than max_num_molecules
        # there are two cases:
        # 1. we reached max_num_molecules within the last batch (num_store < len(batch))
        # 2. we reached max_num_molecules exactly at the end of a batch (num_store == len(batch))
        #    -> we need to check if there are more entries in the source

        # case 1:
        too_many_molecules = num_store < len(batch)

        # case 2:
        try:
            # try to get another entry
            next(source)

            # if we get here, there was another entry and we need to send a warning
            too_many_molecules = True
        except StopIteration:
            pass

        # send a warning message if there were more molecules in the job than allowed
        if too_many_molecules:
            yield {
                "topic": "logs",
                "message": LogMessage(
                    job_id=self._job_id,
                    message_type="warning",
                    message=(
                        f"The provided job contains more than "
                        f"{self._max_num_molecules} input structures. Only the "
                        f"first {self._max_num_molecules} will be processed."
                    ),
                ),
            }

        # send a tuple to topic "logs" with the overall size of the job
        yield {
            "topic": "logs",
            "message": LogMessage(
                job_id=self._job_id,
                message_type="report_job_size",
                num_entries=num_entries,
                num_checkpoints=num_checkpoints,
            ),
        }

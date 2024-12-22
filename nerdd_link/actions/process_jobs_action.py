import logging
from pickle import dump
from typing import Any

from nerdd_module.input import DepthFirstExplorer
from nerdd_module.model import ReadInputStep
from rdkit.Chem import Mol
from rdkit.Chem.PropertyMol import PropertyMol

from ..channels import Channel
from ..files import FileSystem
from ..types import CheckpointMessage, JobMessage, LogMessage
from ..utils import batched
from .action import Action

__all__ = ["ProcessJobsAction"]

logger = logging.getLogger(__name__)


class ProcessJobsAction(Action[JobMessage]):
    # Accept new jobs (on the "<job_type>-jobs" topic). For each job, the program
    # iterates through all molecules in the input (files), writes them as batches
    # into checkpoint files and sends checkpoint messages (for each batch) to the
    # "<job_type>-checkpoints" topic. Also, the number of molecules read is
    # reported to the topic "job-sizes".

    def __init__(
        self,
        channel: Channel,
        checkpoint_size: int,
        max_num_molecules: int,
        num_test_entries: int,
        ratio_valid_entries: float,
        maximum_depth: int,
        max_num_lines_mol_block: int,
        data_dir: str,
    ) -> None:
        super().__init__(channel.jobs_topic())
        # relevant for chunking
        self._checkpoint_size = checkpoint_size
        self._max_num_molecules = max_num_molecules
        # parameters of DepthFirstExplorer
        self._num_test_entries = num_test_entries
        self._ratio_valid_entries = ratio_valid_entries
        self._maximum_depth = maximum_depth
        # used as kwargs in DepthFirstExplorer
        self._max_num_lines_mol_block = max_num_lines_mol_block
        self._file_system = FileSystem(data_dir)

    async def _process_message(self, message: JobMessage) -> None:
        job_id = message.id
        job_type = message.job_type
        logger.info(f"Received a new job {job_id} of type {job_type}")

        # the input file to the job is stored in a designated sources directory
        # (the file is allowed to reference other files, but setting the data_dir
        # to the sources directory ensures that we never read files outside of the
        # sources directory)
        data_dir = self._file_system.get_sources_dir()

        # create a reader (explorer) for the input file
        explorer = DepthFirstExplorer(
            num_test_entries=self._num_test_entries,
            threshold=self._ratio_valid_entries,
            maximum_depth=self._maximum_depth,
            # extra args
            max_num_lines_mol_block=self._max_num_lines_mol_block,
            data_dir=data_dir,
        )

        read_input_step = ReadInputStep(explorer, message.source_id)

        # read the input file
        entries = read_input_step()

        # iterate through the entries
        # create batches of size checkpoint_size
        # limit the number of molecules to max_num_molecules
        batches = batched(entries, self._checkpoint_size)
        num_entries = 0
        num_checkpoints = 0
        for i, batch in enumerate(batches):
            # max_num_molecules might be reached within the batch
            num_store = min(len(batch), self._max_num_molecules - num_entries)

            # store batch in data_dir
            with self._file_system.get_checkpoint_file_handle(job_id, i, "wb") as f:
                results = list(batch[:num_store])

                # TODO: use a model for storing the batches

                # check all items for mol values and use PropertyMol for those
                # in order to keep molecular properties (thanks, RDKit! :/ )
                def _check_value(value: Any) -> Any:
                    if isinstance(value, Mol):
                        return PropertyMol(value)
                    return value

                def _check_item(item: dict) -> dict:
                    return {key: _check_value(value) for key, value in item.items()}

                results = [_check_item(item) for item in results]

                dump(results, f)

            # send a tuple to topic cypstrate-checkpoints
            await self.channel.checkpoints_topic(job_type).send(
                CheckpointMessage(
                    job_id=job_id,
                    checkpoint_id=i,
                    params=message.params,
                )
            )

            num_entries += num_store
            num_checkpoints += 1

            if num_entries >= self._max_num_molecules:
                break

        logger.info(f"Wrote {i+1} checkpoints containing {num_entries} entries for job {job_id}")

        # send a warning message if there were more molecules in the job than allowed
        too_many_molecules = num_store < len(batch)
        try:
            # try to get another entry
            next(entries)

            # if we get here, there was another entry and we need to send a warning
            too_many_molecules = True
        except StopIteration:
            pass

        if too_many_molecules:
            await self.channel.logs_topic().send(
                LogMessage(
                    job_id=job_id,
                    message_type="warning",
                    message=(
                        f"The provided job contains more than "
                        f"{self._max_num_molecules} input structures. Only the "
                        f"first {self._max_num_molecules} will be processed."
                    ),
                )
            )

        # at the end, send a tuple to topic job-sizes with the overall size
        # of the job
        await self.channel.logs_topic().send(
            LogMessage(
                job_id=job_id,
                message_type="report_job_size",
                num_entries=num_entries,
                num_checkpoints=num_checkpoints,
            )
        )

import logging
import os
from asyncio import get_running_loop, to_thread

from nerdd_module import DepthFirstExplorer, ReadInputStep, WriteOutputStep

from ..channels import Channel
from ..files import FileSystem
from ..steps import WriteCheckpointsStep
from ..types import CheckpointMessage, JobMessage, Tombstone
from ..utils import run_pipeline
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
        num_test_entries: int,
        ratio_valid_entries: float,
        maximum_depth: int,
        max_num_lines_mol_block: int,
        data_dir: str,
    ) -> None:
        super().__init__(channel.jobs_topic())
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
        max_num_molecules = (
            message.max_num_molecules if message.max_num_molecules is not None else 10_000
        )
        checkpoint_size = message.checkpoint_size if message.checkpoint_size is not None else 100
        logger.info(f"Received a new job {job_id} of type {job_type}")

        # create a reader (explorer) for the input file
        explorer = DepthFirstExplorer(
            num_test_entries=self._num_test_entries,
            threshold=self._ratio_valid_entries,
            maximum_depth=self._maximum_depth,
            # extra args
            max_num_lines_mol_block=self._max_num_lines_mol_block,
            # The input file to the job is stored in a designated sources directory. The file is
            # allowed to reference other files, but setting the data_dir to the sources directory
            # ensures that we never read files outside of the sources directory.
            data_dir=self._file_system.get_sources_dir(),
        )

        # create a pipeline for reading and chunking the input
        steps = [
            # read the input file (given by source_id)
            ReadInputStep(explorer, message.source_id),
            # write checkpoints
            WriteCheckpointsStep(
                filesystem=self._file_system,
                job_id=job_id,
                job_type=job_type,
                checkpoint_size=checkpoint_size,
                max_num_molecules=max_num_molecules,
                params=message.params,
            ),
            # send messages to the corresponding topics
            WriteOutputStep(
                output_format="json",
                config=None,  # type: ignore[arg-type]
                channel=self.channel,
                loop=get_running_loop(),
            ),
        ]

        # Run the pipeline in a thread to not block the event loop. We don't need to look out for
        # exceptions, because any exception raised in the thread will be re-raised by asyncio here.
        await to_thread(lambda: run_pipeline(*steps))

    async def _process_tombstone(self, message: Tombstone[JobMessage]) -> None:
        job_id = message.id
        job_type = message.job_type
        logger.info(f"Received a tombstone for job {job_id}")

        for i, path in self._file_system.iter_checkpoint_file_paths(job_id):
            await self.channel.checkpoints_topic(job_type).send(
                Tombstone(
                    CheckpointMessage,
                    job_id=job_id,
                    checkpoint_id=i,
                )
            )

            # delete the checkpoint file if it exists
            # note: it is important that we delete the file at the end of the loop, because we don't
            # want to delete the file without propagating the tombstone first
            if os.path.exists(path):
                os.remove(path)

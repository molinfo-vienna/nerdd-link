import logging
import os
from pickle import dump

from nerdd_module.input import DepthFirstExplorer
from nerdd_module.model import ReadInputStep

from ..channels import Channel
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
        checkpoint_size,
        max_num_molecules,
        num_test_entries,
        ratio_valid_entries,
        maximum_depth,
        max_num_lines_mol_block,
        data_dir,
    ):
        super().__init__(channel.jobs_topic())
        # relevant for chunking
        self.checkpoint_size = checkpoint_size
        self.max_num_molecules = max_num_molecules
        # parameters of DepthFirstExplorer
        self.num_test_entries = num_test_entries
        self.ratio_valid_entries = ratio_valid_entries
        self.maximum_depth = maximum_depth
        # used as kwargs in DepthFirstExplorer
        self.max_num_lines_mol_block = max_num_lines_mol_block
        self.data_dir = data_dir

    def _process_message(self, message: JobMessage) -> None:
        job_id = message.id
        job_type = message.job_type

        # the input file to the job is stored in the directory data_dir/sources/
        # (the file is allowed to reference other files, but setting the data_dir
        # to the sources directory ensures that we never read files outside of the
        # sources directory)
        sources_dir = os.path.join(self.data_dir, "sources")

        # create a reader (explorer) for the input file
        explorer = DepthFirstExplorer(
            num_test_entries=self.num_test_entries,
            threshold=self.ratio_valid_entries,
            maximum_depth=self.maximum_depth,
            # extra args
            max_num_lines_mol_block=self.max_num_lines_mol_block,
            data_dir=sources_dir,
        )

        read_input_step = ReadInputStep(explorer, message.source_id)

        # create a directory for the job
        os.makedirs(f"{self.data_dir}/jobs/{job_id}/input", exist_ok=True)

        # read the input file
        entries = read_input_step()

        # iterate through the entries
        # create batches of size checkpoint_size
        # limit the number of molecules to max_num_molecules
        batches = batched(entries, self.checkpoint_size)
        num_entries = 0
        for i, batch in enumerate(batches):
            # max_num_molecules might be reached within the batch
            num_store = min(len(batch), self.max_num_molecules - num_entries)

            # store batch in data_dir
            with open(f"{self.data_dir}/jobs/{job_id}/input/checkpoint_{i}.pickle", "wb") as f:
                dump(batch[:num_store], f)

            # send a tuple to topic cypstrate-checkpoints
            self.channel.checkpoints_topic(job_type).send(
                CheckpointMessage(
                    job_id=job_id,
                    checkpoint_id=i,
                    params=message.params,
                )
            )

            num_entries += num_store

            if num_entries >= self.max_num_molecules:
                break

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
            self.channel.logs_topic().send(
                LogMessage(
                    job_id=job_id,
                    message_type="warning",
                    message=(
                        f"The provided job contains more than "
                        f"{self.max_num_molecules} input structures. Only the "
                        f"first {self.max_num_molecules} will be processed."
                    ),
                )
            )

        # at the end, send a tuple to topic job-sizes with the overall size
        # of the job
        self.channel.logs_topic().send(
            LogMessage(
                job_id=job_id,
                message_type="report_job_size",
                size=num_entries,
            )
        )

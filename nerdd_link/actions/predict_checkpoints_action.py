import logging
import os
import time
from asyncio import get_running_loop, to_thread

from nerdd_module import Model

from ..channels import Channel
from ..delegates import PredictCheckpointModel
from ..files import FileSystem
from ..types import CheckpointMessage, ResultCheckpointMessage, Tombstone
from .action import Action

__all__ = ["PredictCheckpointsAction"]

logger = logging.getLogger(__name__)


class PredictCheckpointsAction(Action[CheckpointMessage]):
    # Accept a batch of input molecules on the "<job-type>-checkpoints" topic
    # (generated in the previous step) and process them. Results are written to
    # the "results" topic.

    def __init__(self, channel: Channel, model: Model, data_dir: str) -> None:
        super().__init__(channel.checkpoints_topic(model))
        self._model = model
        self._file_system = FileSystem(data_dir)

    async def _process_message(self, message: CheckpointMessage) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        params = message.params

        # job might have been deleted in the meantime, so we check if the job exists
        if not os.path.exists(self._file_system.get_checkpoint_file_path(job_id, checkpoint_id)):
            logger.warning(
                f"Received a checkpoint message for job {job_id} and checkpoint {checkpoint_id}, "
                "but the checkpoint file does not exist. Skipping."
            )
            return

        logger.info(f"Predict checkpoint {checkpoint_id} of job {job_id}")

        # track the time it takes to process the message
        start_time = time.time()

        # remove specific parameter keys that could induce vulnerabilities
        params.pop("input", None)

        # create a wrapper model that
        # * reads the checkpoint file instead of normal input
        # * does preprocessing, prediction, and postprocessing like the encapsulated model
        # * does not write to the specified results file, but to the checkpoints file instead
        # * sends the results to the results topic
        model = PredictCheckpointModel(
            base_model=self._model,
            job_id=job_id,
            file_system=self._file_system,
            checkpoint_id=checkpoint_id,
            channel=self.channel,
            loop=get_running_loop(),
        )

        # read from the checkpoint file
        checkpoints_file = self._file_system.get_checkpoint_file_handle(job_id, checkpoint_id, "rb")

        # Run the prediction in a separate thread to avoid blocking the event loop. We don't need to
        # look out for exceptions, because any exception raised in the thread will be re-raised by
        # asyncio here.
        await to_thread(lambda: model.predict(input=checkpoints_file, **params))

        # None indicates the end of the queue (end of the prediction)
        end_time = time.time()

        await self.channel.result_checkpoints_topic().send(
            ResultCheckpointMessage(
                job_id=job_id,
                checkpoint_id=checkpoint_id,
                elapsed_time_seconds=int(end_time - start_time),
            )
        )

    async def _process_tombstone(self, message: Tombstone[CheckpointMessage]) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        logger.info(f"Received a tombstone for checkpoint {checkpoint_id} of job {job_id}")

        # delete result checkpoint file if it exists
        path = self._file_system.get_results_file_path(job_id, checkpoint_id)
        if os.path.exists(path):
            os.remove(path)

        # Send a tombstone to the results topic to indicate that the prediction is done.
        await self.channel.result_checkpoints_topic().send(
            Tombstone(
                ResultCheckpointMessage,
                job_id=job_id,
                checkpoint_id=checkpoint_id,
            )
        )

    def _get_group_name(self) -> str:
        model_id = self._model.config.id
        return f"predict-checkpoints-{model_id}"

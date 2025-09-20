import asyncio
import concurrent.futures
import logging
import os
import time
from asyncio import Queue

from nerdd_module import Model

from ..channels import Channel
from ..delegates import ReadCheckpointModel
from ..files import FileSystem
from ..types import CheckpointMessage, ResultCheckpointMessage, ResultMessage, Tombstone
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
        self.file_system = FileSystem(data_dir)

    async def _process_message(self, message: CheckpointMessage) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        params = message.params

        # job might have been deleted in the meantime, so we check if the job exists
        if not os.path.exists(self.file_system.get_checkpoint_file_path(job_id, checkpoint_id)):
            logger.warning(
                f"Received a checkpoint message for job {job_id} and checkpoint {checkpoint_id}, "
                "but the checkpoint file does not exist. Skipping."
            )
            return

        # Track the time it takes to process the message
        start_time = time.time()

        logger.info(f"Predict checkpoint {checkpoint_id} of job {job_id}")

        # The Kafka consumers and producers run in the current asyncio event loop and (by
        # observation) it seems that calling the produce method of a Kafka producer in a
        # different event loop / thread / process doesn't seem to work (hangs indefinitely).
        # Therefore, we create a queue in this event loop / thread and other tasks send messages
        # to the queue instead of directly to the Kafka producer. This event loop will wait for
        # new messages in this queue and forward them to the Kafka producer.
        queue: Queue = Queue()

        loop = asyncio.get_running_loop()

        # create a wrapper model that
        # * reads the checkpoint file instead of normal input
        # * does preprocessing, prediction, and postprocessing like the encapsulated model
        # * does not write to the specified results file, but to the checkpoints file instead
        # * sends the results to the results topic
        model = ReadCheckpointModel(
            base_model=self._model,
            job_id=job_id,
            file_system=self.file_system,
            checkpoint_id=checkpoint_id,
            queue=queue,
            loop=loop,
        )

        def _predict() -> None:
            try:
                model.predict(input=None, **params)
            except Exception as e:
                queue.put_nowait(e)
                # indicate the end of the computation
                queue.put_nowait(None)

        # Run the prediction in a separate thread to avoid blocking the event loop.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # predict the checkpoint
            # * assign input=None, because the checkpoint file is provided in ReadCheckpointModel
            future = loop.run_in_executor(
                executor,
                _predict,
            )

            # Wait for the prediction to finish and the results to be sent.
            while True:
                record = await queue.get()
                if record is not None:
                    if isinstance(record, Exception):
                        exception = record
                        # an error occurred during prediction
                        logger.error(f"Error during prediction of job {job_id}", exc_info=exception)

                        # TODO: send an error message to the logs topic
                    await self.channel.results_topic().send(ResultMessage(job_id=job_id, **record))
                else:
                    # None indicates the end of the queue (end of the prediction)
                    end_time = time.time()

                    await self.channel.result_checkpoints_topic().send(
                        ResultCheckpointMessage(
                            job_id=job_id,
                            checkpoint_id=checkpoint_id,
                            elapsed_time_seconds=int(end_time - start_time),
                        )
                    )
                    break

            await future

    async def _process_tombstone(self, message: Tombstone[CheckpointMessage]) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        logger.info(f"Received a tombstone for checkpoint {checkpoint_id} of job {job_id}")

        # delete result checkpoint file if it exists
        path = self.file_system.get_results_file_path(job_id, checkpoint_id)
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

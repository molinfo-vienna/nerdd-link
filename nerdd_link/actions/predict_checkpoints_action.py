import asyncio
import concurrent.futures
import logging
from asyncio import Queue

from nerdd_module import SimpleModel

from ..channels import Channel
from ..delegates import ReadCheckpointModel
from ..files import FileSystem
from ..types import CheckpointMessage, ResultCheckpointMessage, ResultMessage
from .action import Action

__all__ = ["PredictCheckpointsAction"]

logger = logging.getLogger(__name__)


class PredictCheckpointsAction(Action[CheckpointMessage]):
    # Accept a batch of input molecules on the "<job-type>-checkpoints" topic
    # (generated in the previous step) and process them. Results are written to
    # the "results" topic.

    def __init__(self, channel: Channel, model: SimpleModel, data_dir: str) -> None:
        super().__init__(channel.checkpoints_topic(model))
        self._model = model
        self._data_dir = data_dir

    async def _process_message(self, message: CheckpointMessage) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        params = message.params
        logger.info(f"Predict checkpoint {checkpoint_id} of job {job_id}")

        # The Kafka consumers and producers run in the current asyncio event loop and (by
        # observation) it seems that calling the produce method of a Kafka producer in a
        # different event loop / thread / process doesn't seem to work (hangs indefinitely).
        # Therefore, we create a queue in this event loop / thread and other tasks send messages
        # to the queue instead of directly to the Kafka producer. This event loop will wait for
        # new messages in this queue and forward them to the Kafka producer.
        queue: Queue = Queue()

        file_system = FileSystem(self._data_dir)

        loop = asyncio.get_running_loop()

        # create a wrapper model that
        # * reads the checkpoint file instead of normal input
        # * does preprocessing, prediction, and postprocessing like the encapsulated model
        # * does not write to the specified results file, but to the checkpoints file instead
        # * sends the results to the results topic
        model = ReadCheckpointModel(
            base_model=self._model,
            job_id=job_id,
            file_system=file_system,
            checkpoint_id=checkpoint_id,
            queue=queue,
            loop=loop,
        )

        # Run the prediction in a separate thread to avoid blocking the event loop.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # predict the checkpoint
            # assign input=None, because the checkpoint file is provided in ReadCheckpointModel
            future = loop.run_in_executor(executor, lambda: model.predict(input=None, **params))

            # Wait for the prediction to finish and the results to be sent.
            while True:
                record = await queue.get()
                if record is not None:
                    await self.channel.results_topic().send(ResultMessage(job_id=job_id, **record))
                else:
                    await self.channel.result_checkpoints_topic().send(
                        ResultCheckpointMessage(job_id=job_id, checkpoint_id=checkpoint_id)
                    )
                    break

            await future

    def _get_group_name(self) -> str:
        model_id = self._model.get_config().id
        return f"predict-checkpoints-{model_id}"

import asyncio
import concurrent.futures
import logging
from asyncio import Queue

from nerdd_module import Model, SimpleModel

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

    def __init__(self, channel: Channel, model: Model, data_dir: str) -> None:
        super().__init__(channel.checkpoints_topic(model))
        self._model = model
        self._file_system = FileSystem(data_dir)

    async def _process_message(self, message: CheckpointMessage) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        params = message.params
        logger.info(f"Predict checkpoint {checkpoint_id} of job {job_id}")

        # The Kafka consumers and producers run in the current asyncio event loop and (by
        # observation) it seems that calling the produce method of a Kafka producer in a different
        # event loop or thread doesn't seem to work (hangs indefinitely). Therefore, we create a
        # queue in this event loop / thread and send the results from the other thread to the
        # queue.
        queue: Queue = Queue()

        async def send_messages() -> None:
            while True:
                record = await queue.get()
                if record is not None:
                    await self.channel.results_topic().send(ResultMessage(job_id=job_id, **record))
                else:
                    await self.channel.result_checkpoints_topic().send(
                        ResultCheckpointMessage(job_id=job_id, checkpoint_id=checkpoint_id)
                    )
                    break

        def _heavy_work() -> None:
            # create a wrapper model that
            # * reads the checkpoint file instead of normal input
            # * does preprocessing, prediction, and postprocessing like the encapsulated model
            # * does not write to the specified results file, but to the checkpoints file instead
            # * sends the results to the results topic
            model = ReadCheckpointModel(
                base_model=self._model,
                job_id=job_id,
                file_system=self._file_system,
                checkpoint_id=checkpoint_id,
                queue=queue,
            )

            # predict the checkpoint
            model.predict(
                input=None,
                **params,
            )

        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = loop.run_in_executor(pool, _heavy_work)

            # Wait for the prediction to finish and the results to be sent.
            await asyncio.gather(future, send_messages())

    def _get_group_name(self) -> str:
        assert isinstance(self._model, SimpleModel)
        model_id = self._model.get_config().id
        return f"predict-checkpoints-{model_id}"

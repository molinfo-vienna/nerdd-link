import logging
import time
from asyncio import AbstractEventLoop, get_running_loop, to_thread
from typing import IO, Any, Iterable, List, Optional

from nerdd_module import Model
from nerdd_module.config import Configuration
from nerdd_module.steps import Step
from rdkit.Chem import Mol

from ..channels import Channel
from ..steps import (
    AddRecordIdStep,
    ReadPickleStep,
    ReplaceLargePropertiesStep,
    SplitAndMergeStep,
    WrapResultsStep,
)
from ..storage import QueuedWriterStorage, Storage
from ..types import CheckpointMessage, ResultCheckpointMessage, Tombstone
from .action import Action

__all__ = ["PredictCheckpointsAction"]

logger = logging.getLogger(__name__)


class PredictCheckpointsAction(Action[CheckpointMessage]):
    # Accept a batch of input molecules on the "<job-type>-checkpoints" topic
    # (generated in the previous step) and process them. Results are written to
    # the "results" topic.

    def __init__(self, channel: Channel, model: Model, storage: Storage) -> None:
        super().__init__(channel.checkpoints_topic(model))
        self._model = model
        self._storage = storage

    async def _process_message(self, message: CheckpointMessage) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        params = message.params

        # job might have been deleted in the meantime, so we check if the job exists
        if not self._storage.checkpoint_file_exists(job_id, checkpoint_id):
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

        async with QueuedWriterStorage(self._storage) as queued_storage:
            with (
                self._storage.get_checkpoint_file_handle(
                    job_id, checkpoint_id, "rb"
                ) as checkpoint_handle,
                self._storage.get_result_checkpoint_file_handle(
                    job_id, checkpoint_id, "wb"
                ) as result_checkpoint_handle,
            ):
                # create a wrapper model that
                # * reads the checkpoint file instead of normal input
                # * does preprocessing, prediction, and postprocessing like the encapsulated model
                # * writes to the checkpoint file instead of the specified results file
                # * sends the results to the results topic
                model = _PredictCheckpointModel(
                    base_model=self._model,
                    job_id=job_id,
                    storage=queued_storage,
                    result_checkpoint_handle=result_checkpoint_handle,
                    channel=self.channel,
                    loop=get_running_loop(),
                )

                # Run the prediction in a separate thread to avoid blocking the event loop. We don't
                # need to handle exceptions separately because they are re-raised here.
                await to_thread(lambda: model.predict(input=checkpoint_handle, **params))

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
        self._storage.delete_result_checkpoint_file(job_id, checkpoint_id)

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self._model!r}, storage={self._storage!r})"


class _PredictCheckpointModel(Model):
    def __init__(
        self,
        base_model: Model,
        job_id: str,
        storage: Storage,
        result_checkpoint_handle: IO,
        channel: Channel,
        loop: AbstractEventLoop,
    ) -> None:
        super().__init__()
        self._base_model = base_model
        self._job_id = job_id
        self._storage = storage
        self._result_checkpoint_handle = result_checkpoint_handle
        self._channel = channel
        self._loop = loop

    def _get_input_steps(
        self, input: Any, input_format: Optional[str], **kwargs: Any
    ) -> List[Step]:
        return [ReadPickleStep(input)]

    def _get_preprocessing_steps(
        self, input: Any, input_format: Optional[str], **kwargs: Any
    ) -> List[Step]:
        # do preprocessing as the encapsulated model would do
        return self._base_model._get_preprocessing_steps(input, input_format, **kwargs)

    def _get_postprocessing_steps(self, output_format: Optional[str], **kwargs: Any) -> List[Step]:
        # We would like to write the results in two different formats:
        #
        #                             /---> json -> send to results topic
        # predictions -> splitter ---|
        #                            \---> record_list -> save to disk
        #
        send_to_channel_steps = self._base_model._get_postprocessing_steps(
            output_format="json",
            # necessary for ChannelWriter:
            channel=self._channel,
            loop=self._loop,
            # necessary for other preprocessing steps:
            model=self._base_model,
            **kwargs,
        )

        # we have to insert additional steps before sending to channel
        send_to_channel_steps = [
            *send_to_channel_steps[:-1],
            # replace large properties with file references
            ReplaceLargePropertiesStep(
                self._base_model._get_config().get_dict(), self._storage, self._job_id
            ),
            # add record ids
            AddRecordIdStep(self._job_id),
            # wrap results in ResultMessage
            WrapResultsStep(),
            # send to results topic
            send_to_channel_steps[-1],
        ]

        file_writing_steps = self._base_model._get_postprocessing_steps(
            output_format="pickle", output_file=self._result_checkpoint_handle, **kwargs
        )

        return [
            SplitAndMergeStep(
                send_to_channel_steps,
                file_writing_steps,
                queue_length=10000,
            )
        ]

    def _predict_mols(self, mols: List[Mol], **kwargs: Any) -> Iterable[dict]:
        # do prediction as the encapsulated model would do
        return self._base_model._predict_mols(mols, **kwargs)

    def _get_config(self) -> Configuration:
        # return the configuration of the encapsulated model
        return self._base_model._get_config()

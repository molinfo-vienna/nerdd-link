import logging

from nerdd_module import Model

from ..channels import Channel
from ..delegates import ReadCheckpointModel
from ..files import FileSystem
from ..types import CheckpointMessage
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
            channel=self.channel,
        )

        # predict the checkpoint
        model.predict(
            input=None,
            **params,
        )

    def _get_group_name(self) -> str:
        model_name = self._model.__class__.__name__
        return model_name

import os

from nerdd_module import Model
from stringcase import spinalcase

from ..channels import Channel
from ..delegates import ReadCheckpointModel
from ..types import CheckpointMessage
from .action import Action

__all__ = ["PredictCheckpointsAction"]


class PredictCheckpointsAction(Action[CheckpointMessage]):
    # Accept a batch of input molecules on the "<job-type>-checkpoints" topic
    # (generated in the previous step) and process them. Results are written to
    # the "results" topic.

    def __init__(self, channel: Channel, model: Model, data_dir: str) -> None:
        super().__init__(channel.checkpoints_topic(model))
        self.model = model
        self.data_dir = data_dir

    def _process_message(self, message: CheckpointMessage) -> None:
        job_id = message.job_id
        checkpoint_id = message.checkpoint_id
        params = message.params

        # the input file to the job is stored in the file data_dir/job_id/input/
        checkpoints_file = f"{self.data_dir}/jobs/{job_id}/input/checkpoint_{checkpoint_id}.pickle"
        checkpoint_results_file = (
            f"{self.data_dir}/jobs/{job_id}/results/checkpoint_{checkpoint_id}.pickle"
        )

        # create the results directory
        os.makedirs(f"{self.data_dir}/jobs/{job_id}/results", exist_ok=True)

        # create a model that reads the checkpoint file
        model = ReadCheckpointModel(
            base_model=self.model,
            job_id=job_id,
            checkpoint_id=checkpoint_id,
            channel=self.channel,
            checkpoints_file=checkpoints_file,
            results_file=checkpoint_results_file,
        )

        # predict the checkpoint
        model.predict(
            input=None,
            **params,
        )

    def _get_group_name(self):
        model_name = spinalcase(self.model.__class__.__name__)
        return model_name

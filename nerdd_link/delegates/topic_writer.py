from typing import Iterable

from nerdd_module import Model, Writer

from ..channels import Channel
from ..types import ResultCheckpointMessage, ResultMessage

__all__ = ["TopicWriter"]


class TopicWriter(Writer, output_format="json"):
    def __init__(self, model: Model, job_id: str, checkpoint_id: int, channel: Channel):
        self.job_id = job_id
        self.checkpoint_id = checkpoint_id
        self.results_topic = channel.results_topic()
        self.result_checkpoints_topic = channel.result_checkpoints_topic(model)

    def write(self, records: Iterable[dict]) -> None:
        for record in records:
            self.results_topic.send(ResultMessage(job_id=self.job_id, **record))
        self.result_checkpoints_topic.send(
            ResultCheckpointMessage(job_id=self.job_id, checkpoint_id=self.checkpoint_id)
        )

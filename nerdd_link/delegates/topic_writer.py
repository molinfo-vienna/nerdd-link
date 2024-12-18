import asyncio
from typing import Iterable

from nerdd_module import Writer

from ..channels import Channel
from ..types import ResultCheckpointMessage, ResultMessage

__all__ = ["TopicWriter"]


class TopicWriter(Writer, output_format="json"):
    def __init__(self, job_id: str, checkpoint_id: int, channel: Channel):
        self.job_id = job_id
        self.checkpoint_id = checkpoint_id
        self.results_topic = channel.results_topic()
        self.result_checkpoints_topic = channel.result_checkpoints_topic()

    def write(self, records: Iterable[dict]) -> None:
        async def send_messages() -> None:
            for record in records:
                await self.results_topic.send(ResultMessage(job_id=self.job_id, **record))
            await self.result_checkpoints_topic.send(
                ResultCheckpointMessage(job_id=self.job_id, checkpoint_id=self.checkpoint_id)
            )

        asyncio.run(send_messages())

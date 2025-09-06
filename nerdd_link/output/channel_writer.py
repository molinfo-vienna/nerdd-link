import logging
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from typing import Iterable

from nerdd_module import Writer, WriterConfig

from ..channels import Channel

__all__ = ["ChannelWriter"]

logger = logging.getLogger(__name__)


class ChannelWriter(Writer):
    def __init__(self, channel: Channel, loop: AbstractEventLoop) -> None:
        super().__init__()
        self._channel = channel
        self._loop = loop

    def write(self, records: Iterable[dict]) -> None:
        for message_spec in records:
            topic_name = message_spec.get("topic", None)
            message = message_spec.get("message", None)

            if topic_name is None:
                logger.warning(f"Message spec {message_spec} does not contain a topic. Skipping.")
                continue

            topic = self._channel.topic_by_name(topic_name)

            if message is None or type(message) is not topic.message_type:
                logger.warning(
                    f"Message spec {message_spec} does not contain a valid message for topic"
                    f"{topic_name}. Skipping."
                )
                continue

            # The Kafka consumers and producers run in another asyncio event loop and (by
            # observation) it seems that calling the produce method of a Kafka producer in a
            # different event loop / thread / process doesn't seem to work (hangs indefinitely).
            # Therefore, we use run_coroutine_threadsafe to send the message in the correct event
            # loop.
            future = run_coroutine_threadsafe(topic.send(message), self._loop)

            # Wait for the message to be sent
            future.result()

    config = WriterConfig(output_format="json")

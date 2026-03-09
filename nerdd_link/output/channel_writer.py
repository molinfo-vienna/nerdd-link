from __future__ import annotations

import logging
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from time import monotonic
from typing import TYPE_CHECKING, Any, Iterable, Optional

from nerdd_module.output import Writer, WriterConfig

from ..utils import CommandQueueThread, command

if TYPE_CHECKING:
    from ..channels import Channel, Topic
    from ..types import Message

__all__ = ["ChannelWriter"]

logger = logging.getLogger(__name__)


class _ChannelWriterWorker(CommandQueueThread):
    def __init__(
        self,
        loop: AbstractEventLoop,
        max_batch_size: int = 1000,
        max_batch_delay: float = 0.1,
        max_queue_size: int = 1_000_000,
    ) -> None:
        if max_batch_size <= 0:
            raise ValueError("max_batch_size must be greater than zero.")

        super().__init__(
            name="channel-writer",
            max_queue_size=max_queue_size,
            idle_timeout=max_batch_delay,
        )

        self._loop = loop
        self._max_batch_size = max_batch_size
        self._max_batch_delay = max_batch_delay
        self._batch: list[tuple[Topic[Any], Message]] = []
        self._batch_started_at = monotonic()
        self._send_error: Optional[BaseException] = None

    @command(fire_and_forget=True)
    def write(self, topic: Topic[Any], message: Message) -> None:
        if self._send_error is not None:
            return

        now = monotonic()
        if len(self._batch) > 0 and now - self._batch_started_at >= self._max_batch_delay:
            self._send_batch()

        if len(self._batch) == 0:
            self._batch_started_at = now

        self._batch.append((topic, message))
        if len(self._batch) >= self._max_batch_size:
            self._send_batch()

    def _on_idle(self) -> None:
        if len(self._batch) > 0:
            self._send_batch()

    def _shutdown(self) -> None:
        if len(self._batch) > 0:
            self._send_batch()
        if self._send_error is not None:
            raise self._send_error

    def _send_batch(self) -> None:
        batch = self._batch
        self._batch = []

        try:
            future = run_coroutine_threadsafe(self._send_messages(batch), self._loop)
            future.result()
        except BaseException as error:
            self._send_error = error

    async def _send_messages(self, batch: list[tuple[Topic[Any], Message]]) -> None:
        for topic, message in batch:
            await topic.send(message)


class ChannelWriter(Writer):
    def __init__(
        self,
        channel: Optional[Channel] = None,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        super().__init__()
        self._channel = channel
        self._loop = loop

    def write(self, records: Iterable[dict]) -> None:
        # We didn't require channel and loop in constructor, because ChannelWriter is automatically
        # registered and instantiated in nerdd_module. For that reason, ChannelWriter needs to
        # work with empty arguments. However, it will only be actively used when the user
        # explicitly requests output_format="json". And in that case, we still need to check if
        # channel and event loop are provided.
        if self._channel is None or self._loop is None:
            raise RuntimeError(
                "ChannelWriter is not properly initialized with a channel and event loop."
            )

        worker = _ChannelWriterWorker(self._loop)
        worker.start()

        failed = False
        try:
            for message_spec in records:
                topic_name = message_spec.get("topic")
                message = message_spec.get("message")

                if topic_name is None:
                    logger.warning(
                        f"Message spec {message_spec} does not contain a topic. Skipping."
                    )
                    continue

                topic = self._channel.topic_by_name(topic_name)

                if message is None or type(message) is not topic.message_type:
                    logger.warning(
                        f"Message spec {message_spec} does not contain a valid message for topic"
                        f"{topic_name}. Skipping."
                    )
                    continue

                worker.write(topic, message)
        except BaseException:
            failed = True
            raise
        finally:
            try:
                worker.stop().result()
            except BaseException:
                if not failed:
                    raise
            finally:
                worker.join()

    config = WriterConfig(output_format="json")

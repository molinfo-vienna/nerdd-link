import logging
from abc import ABC
from asyncio import CancelledError
from typing import Generic, List, TypeVar, Union

from stringcase import spinalcase

from ..channels import Channel, Topic
from ..types import Message, Tombstone

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Message)


class Action(ABC, Generic[T]):
    def __init__(self, input_topic: Topic[T], batch_size: int = 1) -> None:
        self._input_topic = input_topic
        self._batch_size = batch_size

    async def run(self) -> None:
        consumer_group = spinalcase(self._get_group_name())
        async for message_batch in self._input_topic.receive(
            consumer_group, batch_size=self._batch_size
        ):
            try:
                await self._process_message_batch(message_batch)
            except CancelledError:
                # the consumer was cancelled, stop processing messages
                break
            except Exception as e:
                # If any exception is raised in _process_message, we will stop processing messages.
                # Especially, the message won't be committed.
                logger.exception(
                    f"An error occurred while processing message batch {message_batch}",
                    exc_info=e,
                )
                raise

    async def _process_message_batch(self, message_batch: List[Union[T, Tombstone[T]]]) -> None:
        messages = []
        tombstones = []

        for message in message_batch:
            if isinstance(message, Tombstone):
                tombstones.append(message)
            else:
                messages.append(message)

        await self._process_messages(messages)
        await self._process_tombstones(tombstones)

    async def _process_messages(self, messages: List[T]) -> None:
        for message in messages:
            await self._process_message(message)

    async def _process_tombstones(self, tombstones: List[Tombstone[T]]) -> None:
        for tombstone in tombstones:
            await self._process_tombstone(tombstone)

    async def _process_message(self, message: T) -> None:
        pass

    async def _process_tombstone(self, message: Tombstone[T]) -> None:
        pass

    @property
    def channel(self) -> Channel:
        return self._input_topic.channel

    def _get_group_name(self) -> str:
        return self.__class__.__name__

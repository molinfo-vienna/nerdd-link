import logging
from abc import ABC, abstractmethod
from asyncio import CancelledError
from typing import Generic, TypeVar

from stringcase import spinalcase

from ..channels import Channel, Topic
from ..types import Message, Tombstone

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Message)


class Action(ABC, Generic[T]):
    def __init__(self, input_topic: Topic[T]):
        self._input_topic = input_topic

    async def run(self) -> None:
        consumer_group = spinalcase(self._get_group_name())
        async for message in self._input_topic.receive(consumer_group):
            try:
                if isinstance(message, Tombstone):
                    await self._process_tombstone(message)
                else:
                    await self._process_message(message)
            except CancelledError:
                # the consumer was cancelled, stop processing messages
                break
            except Exception as e:
                # If any exception is raised in _process_message, we will stop processing messages.
                # Especially, the message won't be committed.
                logger.exception(
                    "An error occurred while processing message %s: %s",
                    message,
                    e,
                )
                raise

    async def _process_messages(self, messages: list[T]) -> None:
        for message in messages:
            await self._process_message(message)

    @abstractmethod
    async def _process_message(self, message: T) -> None:
        pass

    async def _process_tombstone(self, message: Tombstone[T]) -> None:
        pass

    @property
    def channel(self) -> Channel:
        return self._input_topic.channel

    def _get_group_name(self) -> str:
        return self.__class__.__name__

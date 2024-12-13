import logging
from abc import ABC, abstractmethod
from asyncio import CancelledError
from typing import Generic, TypeVar

from stringcase import spinalcase

from ..channels import Channel, Topic
from ..types import Message

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Message)


class Action(ABC, Generic[T]):
    def __init__(self, input_topic: Topic[T]):
        self._input_topic = input_topic

    async def run(self) -> None:
        consumer_group = spinalcase(self._get_group_name())
        async for message in self._input_topic.receive(consumer_group):
            try:
                await self._process_message(message)
            except CancelledError:
                # the consumer was cancelled, stop processing messages
                break
            except Exception:
                # log the error and continue processing the next message
                logger.error("Error processing message", exc_info=True)

    @abstractmethod
    async def _process_message(self, message: T) -> None:
        pass

    @property
    def channel(self) -> Channel:
        return self._input_topic.channel

    def _get_group_name(self) -> str:
        return self.__class__.__name__

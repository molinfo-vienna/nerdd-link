import logging
from typing import AsyncIterable, List, Tuple

from ..types import Message
from ..utils import ObservableList
from .channel import Channel

__all__ = ["MemoryChannel"]

logger = logging.getLogger(__name__)


class MemoryChannel(Channel):
    def __init__(self) -> None:
        super().__init__()
        self._messages = ObservableList[Tuple[str, Message]]()

    def get_produced_messages(self) -> List[Tuple[str, Message]]:
        return self._messages.get_items()

    async def _iter_messages(self, topic: str, consumer_group: str) -> AsyncIterable[Message]:
        async for _, new in self._messages.changes():
            assert new is not None
            (t, message) = new
            if topic == t:
                yield message

    async def _send(self, topic: str, message: Message) -> None:
        logger.info(f"Send message to topic {topic}")
        self._messages.append((topic, message))

    async def stop(self) -> None:
        await self._messages.stop()

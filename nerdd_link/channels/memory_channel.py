import logging
from asyncio import Lock
from typing import AsyncIterable, Dict, List, Optional, Tuple

from ..utils import ObservableList
from .channel import Channel

__all__ = ["MemoryChannel"]

logger = logging.getLogger(__name__)


class MemoryChannel(Channel):
    def __init__(self) -> None:
        super().__init__()
        self._messages = ObservableList[Tuple[str, Optional[tuple], Optional[dict]]]()
        self._watermarks: Dict[Tuple[str, str], int] = dict()
        self._lock = Lock()

    def get_produced_messages(self) -> List[Tuple[str, Optional[tuple], Optional[dict]]]:
        return self._messages.get_items()

    async def _iter_messages(
        self, topic: str, consumer_group: str
    ) -> AsyncIterable[Tuple[Optional[tuple], Optional[dict]]]:
        num_retrieved = 0
        async for _, new in self._messages.changes():
            assert new is not None
            (t, key, value) = new
            if topic == t:
                num_retrieved += 1
                async with self._lock:
                    num_consumed = self._watermarks.get((topic, consumer_group), 0)
                    if num_retrieved <= num_consumed:
                        # message was already consumed by another member of the consumer_group
                        # -> skip this message
                        continue
                    try:
                        yield key, value
                    finally:
                        self._watermarks[(topic, consumer_group)] = num_consumed + 1

    async def _send(self, topic: str, key: Optional[tuple], value: Optional[dict]) -> None:
        logger.info(f"Send message to topic {topic}")
        self._messages.append((topic, key, value))

    async def stop(self) -> None:
        await self._messages.stop()

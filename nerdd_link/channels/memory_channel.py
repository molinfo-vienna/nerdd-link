import asyncio
import logging
from typing import AsyncIterable, Generic, List, Optional, Tuple, TypeVar

from nerdd_link.channels import Channel
from nerdd_link.types import Message

__all__ = ["MemoryChannel", "ObservableList"]

logger = logging.getLogger(__name__)

T = TypeVar("T")

Change = Tuple[Optional[T], Optional[T]]


class ObservableList(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
        self._changes: List[Change] = []
        self._event = asyncio.Event()
        self._stopped = False

    def append(self, item: T) -> None:
        self._apply_change((None, item))
        self._event.set()  # Notify all readers
        self._event.clear()

    def update(self, old_item: T, new_item: T) -> None:
        self._apply_change((old_item, new_item))
        self._event.set()
        self._event.clear()

    def remove(self, item: T) -> None:
        self._apply_change((item, None))
        self._event.set()
        self._event.clear()

    def _apply_change(self, change: Change) -> None:
        # apply the change to the list of items
        old, new = change
        if old is not None and new is not None:
            self._items[self._items.index(old)] = new
        if old is not None:
            self._items.remove(old)
        if new is not None:
            self._items.append(new)

        # add change to the list of changes
        self._changes.append(change)

    def __len__(self) -> int:
        return len(self._items)

    def get_items(self) -> List[T]:
        return self._items

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    async def changes(self) -> AsyncIterable[Change]:
        processed = 0
        while not self._stopped:  # Check if the channel is stopped
            if len(self._changes) <= processed:
                await self._event.wait()

            # Return all items from last_read_index onward
            new_changes = self._changes[processed:]

            for change in new_changes:
                yield change
                processed += 1

    async def stop(self) -> None:
        self._stopped = True

        # This will unblock the async iterator. It will go through the loop once more and process an
        # empty list. At the start of the next iteration, it will see that the channel is stopped
        # and exit.
        self._event.set()


class MemoryChannel(Channel):
    def __init__(self) -> None:
        super().__init__()
        self._messages: ObservableList[Tuple[str, Message]] = ObservableList()

    def get_produced_messages(self) -> List[Tuple[str, Message]]:
        return self._messages.get_items()

    async def _iter_messages(self, topic: str, consumer_group: str) -> AsyncIterable[Message]:
        async for _, (t, message) in self._messages.changes():
            if topic == t:
                yield message

    async def _send(self, topic: str, message: Message) -> None:
        logger.info(f"Send message to topic {topic}")
        self._messages.append((topic, message))

    async def stop(self) -> None:
        await self._messages.stop()

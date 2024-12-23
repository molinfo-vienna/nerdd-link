import asyncio
from typing import AsyncIterable, Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T")

__all__ = ["ObservableList"]


class ObservableList(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
        self._changes: List[Tuple[Optional[T], Optional[T]]] = []
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

    def _apply_change(self, change: Tuple[Optional[T], Optional[T]]) -> None:
        # apply the change to the list of items
        old, new = change
        if old is not None and new is not None:
            self._items[self._items.index(old)] = new
        elif old is not None:
            self._items.remove(old)
        elif new is not None:
            self._items.append(new)

        # add change to the list of changes
        self._changes.append(change)

    def __len__(self) -> int:
        return len(self._items)

    def get_items(self) -> List[T]:
        return self._items

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    async def changes(self) -> AsyncIterable[Tuple[Optional[T], Optional[T]]]:
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

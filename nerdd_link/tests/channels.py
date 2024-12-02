import asyncio
from ast import literal_eval
from typing import AsyncIterable, Generic, List, TypeVar

import pytest_asyncio
from pytest_bdd import parsers, then, when

from nerdd_link.channels import Channel
from nerdd_link.types import Message

from .async_step import async_step

T = TypeVar("T")


class ObservableList(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
        self._event = asyncio.Event()
        self._stopped = False

    def append(self, item: T):
        self._items.append(item)
        self._event.set()  # Notify all readers
        self._event.clear()

    def __len__(self):
        return len(self._items)

    def get_items(self) -> List[T]:
        return self._items

    def __getitem__(self, index):
        return self._items[index]

    async def __aiter__(self) -> AsyncIterable[T]:
        processed = 0
        while not self._stopped:  # Check if the channel is stopped
            if len(self._items) <= processed:
                await self._event.wait()

            # Return all items from last_read_index onward
            new_items = self._items[processed:]

            for item in new_items:
                yield item
                processed += 1

    async def stop(self):
        self._stopped = True
        self._event.set()


class DummyChannel(Channel):
    def __init__(self):
        super().__init__()
        self._messages = ObservableList()

    async def push_message(self, topic, message):
        self._messages.append((topic, message))

    def get_produced_messages(self):
        return self._messages.get_items()

    async def _iter_messages(
        self, topic: str, consumer_group: str
    ) -> AsyncIterable[Message]:
        async for t, message in self._messages:
            if topic == t:
                yield Message(**message)

    async def _send(self, topic, message):
        await self.push_message(topic, message.model_dump())

    async def stop(self):
        await self._messages.stop()


@pytest_asyncio.fixture(scope="function")
async def channel():
    channel = DummyChannel()
    yield channel
    await channel.stop()


@when(
    parsers.parse(
        "the channel receives a message on topic '{topic}' with content\n{message}"
    )
)
@async_step
async def receive_message(channel, topic, message):
    message = literal_eval(message)
    await channel.push_message(topic, message)


@then(
    parsers.parse(
        "the channel sends a message on topic '{topic}' with content\n{message}"
    )
)
def check_exists_message_with_content(channel, topic, message):
    message = literal_eval(message)
    messages = channel.get_produced_messages()
    found = False
    for t, m in messages:
        if t == topic and m == message:
            found = True
            break
    assert found, f"Message {message} not found on topic {topic}."


@then(parsers.parse("the channel sends {num:d} messages on topic '{topic}'"))
def check_number_of_messages(channel, num, topic):
    messages = channel.get_produced_messages()
    count = 0
    for t, _ in messages:
        if t == topic:
            count += 1
    assert count == num, f"Expected {num} messages on topic {topic}, got {count}."


@then(
    parsers.parse(
        "the channel sends a message on topic '{topic}' containing\n{message}"
    )
)
def check_exists_message_containing(channel, topic, message):
    message = literal_eval(message)
    messages = channel.get_produced_messages()
    found = False
    for t, m in messages:
        if t == topic:
            for key, value in message.items():
                if key not in m or m[key] != value:
                    break
            else:
                found = True
                break
    assert found, f"No message containing {message} found on topic {topic}."


@then(parsers.parse("the channel sends exactly {num:d} messages"))
def check_total_number_of_messages(channel, num):
    messages = channel.get_produced_messages()
    assert len(messages) == num, f"Expected {num} messages, got {len(messages)}."

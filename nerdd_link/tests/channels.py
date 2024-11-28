import asyncio
from ast import literal_eval
from typing import AsyncIterable

import pytest_asyncio
from pytest_bdd import parsers, then, when

from nerdd_link.channels import Channel
from nerdd_link.types import Message

from .async_step import async_step


class DummyChannel(Channel):
    def __init__(self):
        super().__init__()
        self._messages = []
        self._event = asyncio.Event()
        self._stopped = False  # Add a flag to indicate if the channel is stopped

    async def push_message(self, topic, message):
        self._messages.append((topic, message))
        self._event.set()  # Notify all readers
        self._event.clear()

    def get_produced_messages(self):
        return self._messages

    async def _iter_messages(
        self, topic: str, consumer_group: str
    ) -> AsyncIterable[Message]:
        processed = 0
        while not self._stopped:  # Check if the channel is stopped
            if len(self._messages) <= processed:
                await self._event.wait()

            # Return all items from last_read_index onward
            new_messages = self._messages[processed:]

            for t, message in new_messages:
                if t == topic:
                    yield Message(**message)
                processed += 1

    async def _send(self, topic, message):
        await self.push_message(topic, message.model_dump())

    async def stop(self):
        self._stopped = True
        self._event.set()  # Wake up any waiting coroutines


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

import logging
from ast import literal_eval

import pytest_asyncio
from pytest_bdd import parsers, then, when

from nerdd_link import MemoryChannel, Message

from .async_step import async_step

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope="function")
async def channel():
    async with MemoryChannel() as channel:
        yield channel


@when(
    parsers.parse(
        "the channel receives a message on topic '{topic}' with content\n{message}"
    )
)
@async_step
async def receive_message(channel, topic, message):
    message = literal_eval(message)
    await channel.send(topic, Message(**message))


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
        if t == topic and m.model_dump() == message:
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
        m = m.model_dump()
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

import logging
from ast import literal_eval

import pytest_asyncio
from pytest_bdd import parsers, then, when

from nerdd_link import (JobMessage, MemoryChannel, Message,
                        ResultCheckpointMessage, SerializationRequestMessage,
                        SystemMessage, Tombstone)

from .async_step import async_step

logger = logging.getLogger(__name__)


def get_message_type_from_topic(topic: str) -> type[Message]:
    if topic == "jobs":
        return JobMessage
    elif topic == "result-checkpoints":
        return ResultCheckpointMessage
    elif topic == "system":
        return SystemMessage
    elif topic == "serialization-requests":
        return SerializationRequestMessage
    else:
        raise ValueError(f"Unknown topic: {topic}")


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
    MessageType = get_message_type_from_topic(topic)
    await channel.send(topic, MessageType(**message))

@when(
    parsers.parse(
        "the channel receives a tombstone on topic '{topic}' with key {key}"
    )
)
@async_step
async def receive_tombstone(channel, topic, key):
    key_tuple = literal_eval(key)
    MessageType = get_message_type_from_topic(topic)
    await channel.send(topic, Tombstone(MessageType, *key_tuple))


@then(
    parsers.parse(
        "the channel sends a message on topic '{topic}' with content\n{message}"
    )
)
def check_exists_message_with_content(channel, topic, message):
    message = literal_eval(message)
    messages = channel.get_produced_messages()
    found = False
    for t, _, value in messages:
        if t == topic and value == message:
            found = True
            break
    assert found, f"Message {message} not found on topic {topic}."


@then(
    parsers.parse(
        "the channel sends a tombstone on topic '{topic}' with key {key}"
    )
)
def check_exists_tombstone_with_key(channel, topic, key):
    key_tuple = literal_eval(key)
    messages = channel.get_produced_messages()
    found = False
    for t, message_key, message_value in messages:
        if t == topic and message_key == key_tuple and message_value is None:
            found = True
            break
    assert found, f"Tombstone with key {key} not found on topic {topic}."


@then(parsers.parse("the channel sends {num:d} messages on topic '{topic}'"))
def check_number_of_messages(channel, num, topic):
    messages = channel.get_produced_messages()
    count = 0
    for t, _, _ in messages:
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
    for t, _, message in messages:
        if t == topic:
            for k, v in message.items():
                if k not in message or v != message[k]:
                    break
            else:
                found = True
                break
    assert found, f"No message containing {message} found on topic {topic}."


@then(parsers.parse("the channel sends exactly {num:d} messages"))
def check_total_number_of_messages(channel, num):
    messages = channel.get_produced_messages()
    assert len(messages) == num, f"Expected {num} messages, got {len(messages)}."

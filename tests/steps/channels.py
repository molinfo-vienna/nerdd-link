from ast import literal_eval

from nerdd_link.channels import Channel
from nerdd_link.types import Message
from pytest_bdd import given, parsers, then, when


class DummyChannel(Channel):
    def __init__(self):
        super().__init__()
        self._messages = []

    def push_message(self, topic, message):
        self._messages.append((topic, message))

    def get_produced_messages(self):
        return self._messages

    def _iter_messages(self, topic, consumer_group=None):
        for t, message in self._messages:
            if t == topic:
                yield Message(**message)

    def _send(self, topic, message):
        print(f"Sending message to topic {topic}")
        self._messages.append((topic, message.model_dump()))


@when(
    parsers.parse(
        "the channel receives a message on topic '{topic}' with content\n{message}"
    )
)
def receive_message(channel, topic, message):
    message = literal_eval(message)
    channel.push_message(topic, message)


@then(
    parsers.parse(
        "the channel sends a message on topic '{topic}' with content\n{message}"
    )
)
def send_message(channel, topic, message):
    message = literal_eval(message)
    messages = channel.get_produced_messages()
    found = False
    for t, m in messages:
        if t == topic and m == message:
            found = True
            break
    assert found, f"Message {message} not found on topic {topic}."


@given(
    parsers.parse("a mocked cummunication channel"),
    target_fixture="channel",
)
def mocked_channel():
    return DummyChannel()


@then(parsers.parse("the channel sends {num:d} messages on topic '{topic}'"))
def send_messages(channel, num, topic):
    messages = channel.get_produced_messages()
    count = 0
    for t, _ in messages:
        if t == topic:
            count += 1
    assert count == num, f"Expected {num} messages on topic {topic}, got {count}."

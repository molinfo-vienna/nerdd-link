from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterator, TypeVar, Union, cast

from nerdd_module import Model
from stringcase import spinalcase  # type: ignore

from ..types import (
    CheckpointMessage,
    JobMessage,
    LogMessage,
    Message,
    ModuleMessage,
    ResultMessage,
    SystemMessage,
)

__all__ = ["Channel", "Topic"]

T = TypeVar("T", bound=Message)


def get_job_type(job_type_or_model: Union[str, Model]) -> str:
    if isinstance(job_type_or_model, Model):
        model = job_type_or_model

        # create topic name from model name by
        # * converting to spinal case, (e.g. "MyModel" -> "my-model")
        # * converting to lowercase (just to be sure) and
        # * removing all characters except dash and alphanumeric characters
        topic_name = spinalcase(model.name)
        topic_name = topic_name.lower()
        topic_name = "".join([c for c in topic_name if str.isalnum(c) or c == "-"])
        return topic_name

    return job_type_or_model


class Topic(Generic[T]):
    def __init__(self, channel: Channel, name: str):
        self._channel = channel
        self._name = name

    def receive(self, consumer_group: str) -> Iterator[T]:
        for msg in self.channel.iter_messages(self._name, consumer_group):
            yield cast(T, msg)

    def send(self, message: T) -> None:
        self.channel.send(self._name, message)

    @property
    def channel(self) -> Channel:
        return self._channel

    def __repr__(self) -> str:
        return f"Topic({self._name})"


class Channel(ABC):
    #
    # RECEIVE
    #
    def iter_messages(self, topic: str, consumer_group: str) -> Iterator[Message]:
        return self._iter_messages(topic, consumer_group)

    @abstractmethod
    def _iter_messages(self, topic: str, consumer_group: str) -> Iterator[Message]:
        pass

    #
    # SEND
    #
    def send(self, topic: str, message: Message) -> None:
        self._send(topic, message)

    @abstractmethod
    def _send(self, topic: str, message: Message) -> None:
        pass

    #
    # TOPICS
    #
    def modules_topic(self) -> Topic[ModuleMessage]:
        return Topic[ModuleMessage](self, "modules")

    def jobs_topic(self) -> Topic[JobMessage]:
        return Topic[JobMessage](self, "jobs")

    def checkpoints_topic(self, job_type_or_model: Union[str, Model]) -> Topic[CheckpointMessage]:
        job_type = get_job_type(job_type_or_model)
        topic_name = f"{job_type}-checkpoints"
        return Topic[CheckpointMessage](self, topic_name)

    def results_topic(self) -> Topic[ResultMessage]:
        return Topic[ResultMessage](self, "results")

    def result_checkpoints_topic(
        self, job_type_or_model: Union[str, Model]
    ) -> Topic[CheckpointMessage]:
        job_type = get_job_type(job_type_or_model)
        topic_name = f"{job_type}-result-checkpoints"
        return Topic[CheckpointMessage](self, topic_name)

    def logs_topic(self) -> Topic[LogMessage]:
        return Topic[LogMessage](self, "logs")

    def system_topic(self) -> Topic[SystemMessage]:
        return Topic[SystemMessage](self, "system")

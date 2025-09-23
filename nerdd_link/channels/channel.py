from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import (
    Any,
    AsyncIterable,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from nerdd_module import Model
from nerdd_module.util import call_with_mappings
from stringcase import snakecase, spinalcase

from ..types import (
    CheckpointMessage,
    JobMessage,
    LogMessage,
    Message,
    ModuleMessage,
    ResultCheckpointMessage,
    ResultMessage,
    SerializationRequestMessage,
    SerializationResultMessage,
    SystemMessage,
    Tombstone,
)

__all__ = ["Channel", "Topic"]

logger = logging.getLogger(__name__)

TMessage = TypeVar("TMessage", bound=Message)


def get_job_type(job_type_or_model: Union[str, Model]) -> str:
    if isinstance(job_type_or_model, Model):
        model = job_type_or_model

        # create topic name from model name by
        # * converting to spinal case, (e.g. "MyModel" -> "my-model")
        # * converting to lowercase (just to be sure) and
        # * removing all characters except dash and alphanumeric characters
        topic_name = spinalcase(model.config.id)
        topic_name = topic_name.lower()
        topic_name = "".join([c for c in topic_name if str.isalnum(c) or c == "-"])
        return topic_name
    else:
        return spinalcase(job_type_or_model)


class Topic(Generic[TMessage]):
    def __init__(self, channel: Channel, name: str, message_type: Type[TMessage]) -> None:
        self._channel = channel
        self._name = name
        self._message_type = message_type

    async def receive(
        self, consumer_group: str, batch_size: int = 1
    ) -> AsyncIterable[List[Union[TMessage, Tombstone[TMessage]]]]:
        async for message_batch in self.channel.iter_messages(
            self._name,
            consumer_group=consumer_group,
            message_type=self._message_type,
            batch_size=batch_size,
        ):
            yield message_batch

    async def send(self, message: Union[TMessage, Tombstone[TMessage]]) -> None:
        await self.channel.send(self._name, message)

    @property
    def channel(self) -> Channel:
        return self._channel

    def __repr__(self) -> str:
        return f"Topic({self._name})"


class Channel(ABC):
    def __init__(self) -> None:
        self._is_running = False

    async def start(self) -> None:
        self._is_running = True
        await self._start()

    async def _start(self) -> None:  # noqa: B027
        pass

    async def stop(self) -> None:
        await self._stop()
        self._is_running = False

    async def _stop(self) -> None:  # noqa: B027
        pass

    async def __aenter__(self) -> Channel:
        await self.start()
        return self

    async def __aexit__(self, exc_type: type, exc_value: Exception, traceback: object) -> None:
        await self.stop()

    #
    # RECEIVE
    #
    async def iter_messages(
        self,
        topic: str,
        consumer_group: str,
        message_type: Type[TMessage],
        batch_size: int = 1,
    ) -> AsyncIterable[List[Union[TMessage, Tombstone[TMessage]]]]:
        if not self._is_running:
            raise RuntimeError("Channel is not running. Call start() first.")

        key_fields = message_type.topic_config.get("key_fields")

        async for key_value_pairs in self._iter_messages(topic, consumer_group, batch_size):
            message_batch: List[Union[TMessage, Tombstone[TMessage]]] = []
            for key, value in key_value_pairs:
                if value is None:
                    assert key is not None, "Key must be provided for tombstone messages"
                    message_batch.append(Tombstone(message_type, *key))
                else:
                    if key_fields is None and key is not None:
                        logger.warning(
                            f"Message type {message_type.__name__} does not have key fields "
                            "defined, but a key was provided. This may lead to unexpected behavior."
                        )

                    message_batch.append(message_type(**value))

            yield message_batch

    # Insane Python quirk: we need to use "def _iter_messages" instead of "async def _iter_messages"
    # here, because the method doesn't use "yield" and so the type checker will assume that the
    # actual type is Coroutine[AsyncIterable[Message], None, None] instead of the type we want:
    # AsyncIterable[Message].
    @abstractmethod
    def _iter_messages(
        self, topic: str, consumer_group: str, batch_size: int
    ) -> AsyncIterable[List[Tuple[Optional[tuple], Optional[dict]]]]:
        pass

    #
    # SEND
    #
    async def send(self, topic: str, message: Union[TMessage, Tombstone[TMessage]]) -> None:
        if not self._is_running:
            raise RuntimeError("Channel is not running. Call start() first.")

        # extract key
        if isinstance(message, Tombstone):
            key_fields = message.message_type.topic_config.get("key_fields")
        else:
            key_fields = message.topic_config.get("key_fields")

        if key_fields is None:
            key = None
        else:
            key = tuple(getattr(message, field) for field in key_fields)

        # extract value
        if isinstance(message, Tombstone):
            value = None
        else:
            value = message.model_dump()

        await self._send(topic, key, value)

    @abstractmethod
    async def _send(self, topic: str, key: Optional[tuple], value: Optional[dict]) -> None:
        pass

    #
    # TOPICS
    #
    def modules_topic(self) -> Topic[ModuleMessage]:
        return Topic(self, "modules", ModuleMessage)

    def jobs_topic(self) -> Topic[JobMessage]:
        return Topic(self, "jobs", JobMessage)

    def checkpoints_topic(self, job_type_or_model: Union[str, Model]) -> Topic[CheckpointMessage]:
        job_type = get_job_type(job_type_or_model)
        topic_name = f"{job_type}-checkpoints"
        return Topic(self, topic_name, CheckpointMessage)

    def results_topic(self) -> Topic[ResultMessage]:
        return Topic(self, "results", ResultMessage)

    def result_checkpoints_topic(self) -> Topic[ResultCheckpointMessage]:
        return Topic(self, "result-checkpoints", ResultCheckpointMessage)

    def serialization_requests_topic(self) -> Topic[SerializationRequestMessage]:
        return Topic(self, "serialization-requests", SerializationRequestMessage)

    def serialization_results_topic(self) -> Topic[SerializationResultMessage]:
        return Topic(self, "serialization-results", SerializationResultMessage)

    def logs_topic(self) -> Topic[LogMessage]:
        return Topic(self, "logs", LogMessage)

    def system_topic(self) -> Topic[SystemMessage]:
        return Topic(self, "system", SystemMessage)

    #
    # META
    #
    _channel_registry: Dict[str, Type["Channel"]] = {}

    @classmethod
    def __init_subclass__(
        cls,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        # check if class ends with "Channel"
        if cls.__name__.endswith("Channel"):
            name = cls.__name__[: -len("Channel")]
            name = snakecase(name)
        else:
            name = cls.__name__

        # register the channel class
        Channel._channel_registry[name] = cls

    @classmethod
    def get_channel(cls, name: str) -> Channel:
        return cls._channel_registry[name]()

    @classmethod
    def create_channel(cls, name: str, **kwargs: Any) -> Channel:
        return call_with_mappings(cls._channel_registry[name], kwargs)

    @classmethod
    def get_channel_names(cls) -> list[str]:
        return list(cls._channel_registry.keys())

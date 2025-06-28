from typing import Any, ClassVar, Dict, Generic, List, Optional, Type, TypeVar

from nerdd_module.polyfills import TypedDict
from pydantic import BaseModel, ConfigDict

__all__ = [
    "CheckpointMessage",
    "JobMessage",
    "ResultMessage",
    "LogMessage",
    "ModuleMessage",
    "SystemMessage",
    "ResultCheckpointMessage",
    "SerializationRequestMessage",
    "SerializationResultMessage",
    "Tombstone",
]

TMessage = TypeVar("TMessage", bound="Message")


class TopicConfig(TypedDict, total=False):
    # The message properties that will be used to compute a message's key, which should be unique
    # within the topic. If log compaction is enabled, only the latest message with a given key will
    # be retained. This mechanism is used for so-called tombstoning, where a message with a
    # specified key and a value of None is sent to indicate that the key should be removed from the
    # topic. In NERDD, this is used to delete computational jobs and their results. If key_fields is
    # not specified, the key will always be None and tombstoning will not be possible.
    key_fields: List[str]


class Message(BaseModel):
    model_config = ConfigDict(extra="allow")
    topic_config: ClassVar[TopicConfig] = TopicConfig()

    IS_TOMBSTONE: ClassVar[bool] = False

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        # __pydantic_init_subclass__ is equivalent to __init_subclass__, but it is called by
        # Pydantic after the class is created, so we can use it to validate the class attributes.
        # For example, cls.model_fields is not available in __init_subclass__.
        super().__pydantic_init_subclass__(**kwargs)

        key_fields = cls.topic_config.get("key_fields")
        if key_fields is not None:
            # check that key_fields is not empty
            if len(key_fields) == 0:
                raise ValueError(f"Message type {cls.__name__} does not have key fields defined.")

            # check that all key fields are present in the message type
            missing_fields = [field for field in key_fields if field not in cls.model_fields]
            if len(missing_fields) > 0:
                raise ValueError(
                    f"Message type {cls.__name__} is missing required key fields: "
                    f"{', '.join(missing_fields)}"
                )


class Tombstone(Generic[TMessage]):
    IS_TOMBSTONE: ClassVar[bool] = True

    def __init__(self, message_type: Type[TMessage], *args: Any, **kwargs: Any) -> None:
        self.message_type = message_type

        if (len(args) == 0) and (len(kwargs) == 0):
            raise ValueError(
                f"Tombstone message for {self.message_type.__name__} must have at least one key "
                f"field defined in the topic config."
            )

        if len(args) > 0 and len(kwargs) > 0:
            raise ValueError(
                f"Tombstone message for {self.message_type.__name__} must have either positional "
                f"or keyword arguments, but not both."
            )

        key_fields = message_type.topic_config.get("key_fields")

        # do not create tombstone messages of message types without key fields
        if key_fields is None:
            raise ValueError(
                f"Message type {self.message_type.__name__} does not have key fields defined. This "
                f"may lead to unexpected behavior."
            )

        if len(args) > 0:
            # check that the key matches the key fields
            if len(args) != len(key_fields):
                raise ValueError(
                    f"Key for message type {self.message_type.__name__} must have "
                    f"{len(key_fields)} elements, but got {len(args)}."
                )

            self.key = dict(zip(key_fields, args))
        else:
            # check that the kwargs keys match the key fields
            for key in kwargs.keys():
                if key not in key_fields:
                    raise ValueError(
                        f"Key field {key} is not defined in the topic config for message type "
                        f"{self.message_type.__name__}."
                    )

            self.key = kwargs

    def __getattr__(self, name: str) -> Any:
        # if name exists as key in self.key, return it
        # otherwise, do the usual attribute lookup
        if name in self.key:
            return self.key[name]
        raise AttributeError(
            f"{self.message_type.__name__} tombstone does not have attribute '{name}'. "
            f"Available keys: {', '.join(self.key.keys())}"
        )


class ModuleMessage(Message):
    id: str

    topic_config: ClassVar[TopicConfig] = TopicConfig(key_fields=["id"])


class CheckpointMessage(Message):
    job_id: str
    checkpoint_id: int
    params: Dict[str, Any]

    topic_config: ClassVar[TopicConfig] = TopicConfig(key_fields=["job_id", "checkpoint_id"])


class ResultCheckpointMessage(Message):
    job_id: str
    checkpoint_id: int
    elapsed_time_seconds: Optional[int] = None

    topic_config: ClassVar[TopicConfig] = TopicConfig(key_fields=["job_id", "checkpoint_id"])


class JobMessage(Message):
    id: str
    job_type: str
    source_id: str
    params: Dict[str, Any]

    topic_config: ClassVar[TopicConfig] = TopicConfig(key_fields=["id", "job_type"])


class SerializationRequestMessage(Message):
    job_id: str
    job_type: str
    params: Dict[str, Any]
    output_format: str

    topic_config: ClassVar[TopicConfig] = TopicConfig(key_fields=["job_id", "output_format"])


class SerializationResultMessage(Message):
    job_id: str
    output_format: str

    topic_config: ClassVar[TopicConfig] = TopicConfig(key_fields=["job_id", "output_format"])


class ResultMessage(Message):
    job_id: str

    model_config = ConfigDict(extra="allow")


class LogMessage(Message):
    job_id: str
    message_type: str

    model_config = ConfigDict(extra="allow")


class SystemMessage(Message):
    pass

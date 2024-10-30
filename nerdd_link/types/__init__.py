from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

__all__ = [
    "CheckpointMessage",
    "JobMessage",
    "ResultMessage",
    "LogMessage",
    "ModuleMessage",
    "SystemMessage",
]


class Message(BaseModel):
    model_config = ConfigDict(extra="allow")


class ModuleMessage(Message):
    name: str


class CheckpointMessage(Message):
    job_id: str
    checkpoint_id: int
    params: Dict[str, Any]


class ResultCheckpointMessage(Message):
    job_id: str
    checkpoint_id: int


class JobMessage(Message):
    id: str
    job_type: str
    source_id: str
    params: Dict[str, Any]
    timestamp: int


class ResultMessage(Message):
    job_id: str


class LogMessage(Message):
    job_id: str
    message_type: str

    model_config = ConfigDict(extra="allow")


class SystemMessage(Message):
    pass

from abc import ABC, abstractmethod
from threading import Event, Thread
from typing import Generic, TypeVar

from stringcase import spinalcase

from ..channels import Channel, Topic
from ..types import Message

T = TypeVar("T", bound=Message)


class Action(ABC, Thread, Generic[T]):
    def __init__(self, input_topic: Topic[T]):
        super().__init__()
        self._stopped = Event()
        self._input_topic = input_topic

    def run(self):
        self._stopped.clear()

        consumer_group = spinalcase(self._get_group_name())

        messages = self._input_topic.receive(consumer_group)

        while not self._stopped.is_set():
            try:
                message = next(messages)
            except StopIteration:
                break
            self._process_message(message)

        self._stopped.set()

    @abstractmethod
    def _process_message(self, message: T) -> None:
        pass

    def wait(self):
        self._stopped.wait()

    def stop(self):
        self._stopped.set()

    @property
    def channel(self) -> Channel:
        return self._input_topic.channel

    def _get_group_name(self) -> str:
        return spinalcase(self.__class__.__name__)

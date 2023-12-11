from abc import ABC, abstractmethod
from typing import Type


class Serializer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _serialize(self, data):
        pass

    def __call__(self, data):
        return self._serialize(data)

    @property
    @abstractmethod
    def type(self) -> Type:
        pass

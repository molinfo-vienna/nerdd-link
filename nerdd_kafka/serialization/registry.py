from typing import Dict, Type

from .serializer import Serializer

__all__ = ["registry", "register_serializer"]

registry: Dict[Type, Serializer] = {}


def register_serializer(serializer: Serializer):
    type = serializer.type()
    registry[type] = serializer

import json

from .registry import registry


class ComplexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        t = type(obj)
        if t in registry:
            return registry[t](obj)
        return obj

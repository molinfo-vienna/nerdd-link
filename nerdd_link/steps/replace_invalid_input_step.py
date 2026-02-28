from nerdd_module.steps import MapStep

__all__ = ["ReplaceInvalidInputStep"]


class ReplaceInvalidInputStep(MapStep):
    def __init__(self, replacement: str) -> None:
        super().__init__()
        self._replacement = replacement

    def _process(self, record: dict) -> dict:
        if record["input_type"] == "unknown" and not isinstance(record["input_text"], str):
            record["input_text"] = self._replacement
        return record

from typing import Any

from nerdd_module import ALL, Converter, ConverterConfig

__all__ = ["PickleConverter"]


class PickleConverter(Converter):
    def _convert(self, input: Any, context: dict) -> Any:
        return input

    config = ConverterConfig(
        data_types=ALL,
        output_formats="pickle",
    )

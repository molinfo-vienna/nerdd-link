from typing import Any

from nerdd_module import ALL, Converter, ConverterConfig
from nerdd_module.config import ResultProperty

__all__ = ["PickleConverter"]


class PickleConverter(Converter):
    def __init__(self, result_property: ResultProperty, output_format: str, **kwargs: Any) -> None:
        super().__init__(result_property, output_format, **kwargs)

    def _convert(self, input: Any, context: dict) -> Any:
        return input

    config = ConverterConfig(
        data_types=ALL,
        output_formats="pickle",
    )

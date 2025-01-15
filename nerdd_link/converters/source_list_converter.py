from typing import Any

from nerdd_module import Converter, ConverterConfig

__all__ = ["SourceListConverter"]


class SourceListConverter(Converter):
    def _convert(self, input: Any, context: dict) -> Any:
        return input

    config = ConverterConfig(
        data_types="source_list",
        output_formats="json",
    )

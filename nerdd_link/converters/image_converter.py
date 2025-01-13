from typing import Any

from nerdd_module import Converter, ConverterConfig

__all__ = ["ImageConverter"]


class ImageConverter(Converter):
    def _convert(self, input: Any, context: dict) -> Any:
        return input

    config = ConverterConfig(
        data_types="image",
        output_formats="json",
    )

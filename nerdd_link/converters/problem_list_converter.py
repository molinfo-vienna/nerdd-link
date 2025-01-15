from typing import Any

from nerdd_module import Converter, ConverterConfig

__all__ = ["ProblemListConverter"]


class ProblemListConverter(Converter):
    def _convert(self, input: Any, context: dict) -> Any:
        return input

    config = ConverterConfig(
        data_types="problem_list",
        output_formats="json",
    )

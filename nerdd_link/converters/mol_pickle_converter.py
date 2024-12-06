from typing import Any

from nerdd_module import Converter, ConverterConfig
from nerdd_module.config import ResultProperty
from rdkit.Chem.PropertyMol import PropertyMol

__all__ = ["MolPickleConverter"]


class MolPickleConverter(Converter):
    def __init__(self, result_property: ResultProperty, output_format: str, **kwargs: Any) -> None:
        super().__init__(result_property, output_format, **kwargs)

    def _convert(self, input: Any, context: dict) -> Any:
        return PropertyMol(input)

    config = ConverterConfig(
        data_types="mol",
        output_formats="pickle",
    )

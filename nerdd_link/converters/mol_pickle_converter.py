from typing import Any

from nerdd_module import Converter, ConverterConfig
from rdkit.Chem import Mol
from rdkit.Chem.PropertyMol import PropertyMol

__all__ = ["MolPickleConverter"]


class MolPickleConverter(Converter):
    def _convert(self, input: Any, context: dict) -> Any:
        if isinstance(input, Mol):
            return PropertyMol(input)
        else:
            return input

    config = ConverterConfig(
        data_types="mol",
        output_formats="pickle",
    )

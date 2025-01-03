from typing import List

from nerdd_module import SimpleModel
from nerdd_module.config import Configuration, DictConfiguration
from rdkit.Chem import Mol

__all__ = ["SerializeJobModel"]


class SerializeJobModel(SimpleModel):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config

    def _get_config(self) -> Configuration:
        return DictConfiguration(self._config)

    def _predict_mols(self, mols: List[Mol]) -> List[dict]:
        return []

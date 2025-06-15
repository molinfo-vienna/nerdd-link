from typing import Any, List

from nerdd_module import Model
from nerdd_module.config import Configuration, DictConfiguration
from rdkit.Chem import Mol

__all__ = ["SerializeJobModel"]


class SerializeJobModel(Model):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config

    def _get_config(self) -> Configuration:
        return DictConfiguration(self._config)

    def _predict_mols(self, mols: List[Mol], **kwargs: Any) -> List[dict]:
        # We will only extract the postprocessing steps of this model and the predict method
        # will never be called.
        return []

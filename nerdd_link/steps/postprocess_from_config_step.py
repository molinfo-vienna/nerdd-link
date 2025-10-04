from typing import Any, Iterator, List, Optional

from nerdd_module import Model, Step
from nerdd_module.config import Configuration, DictConfiguration
from rdkit.Chem import Mol

from ..types import SerializationResultMessage
from ..utils import run_pipeline

__all__ = ["PostprocessFromConfigStep"]


class DummyModel(Model):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config

    def _get_config(self) -> Configuration:
        return DictConfiguration(self._config)

    def _predict_mols(self, mols: List[Mol], **kwargs: Any) -> List[dict]:
        # We will only extract the postprocessing steps of this model and the predict method
        # will never be called.
        return []


class PostprocessFromConfigStep(Step):
    def __init__(
        self,
        config: dict,
        job_id: str,
        output_format: str,
        output_file: Any = None,
        **params: Any,
    ) -> None:
        super().__init__()
        self._config = config
        self._job_id = job_id
        self._output_format = output_format
        self._output_file = output_file
        self._params = params

    def _run(self, source: Optional[Iterator[dict]]) -> Iterator[dict]:
        assert source is not None, "Source iterator cannot be None."

        # extract postprocessing steps specified through the configuration
        model = DummyModel(self._config)
        postprocessing_steps = model._get_postprocessing_steps(
            self._output_format, output_file=self._output_file, **self._params
        )

        run_pipeline(source, *postprocessing_steps)

        # send a message that the serialization is done
        yield {
            "topic": "serialization-results",
            "message": SerializationResultMessage(
                job_id=self._job_id, output_format=self._output_format
            ),
        }

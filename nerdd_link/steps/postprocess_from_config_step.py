from typing import Any, Iterator, List, Optional

from nerdd_module import Model, OutputStep, Step
from nerdd_module.config import Configuration, DictConfiguration
from rdkit.Chem import Mol

from ..types import SerializationResultMessage

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

        # build the pipeline from the list of steps
        pipeline = source
        for t in postprocessing_steps:
            pipeline = t(pipeline)

        output_step = postprocessing_steps[-1]
        assert isinstance(output_step, OutputStep), "The last step must be an OutputStep."

        output_step.get_result()

        # send a message that the serialization is done
        yield {
            "topic": "serialization-results",
            "message": SerializationResultMessage(
                job_id=self._job_id, output_format=self._output_format
            ),
        }

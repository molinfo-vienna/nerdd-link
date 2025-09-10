from asyncio import AbstractEventLoop
from typing import Any, Iterable, List, Optional

from nerdd_module import Model, Step
from nerdd_module.config import Configuration
from rdkit.Chem import Mol

from ..channels import Channel
from ..files import FileSystem
from ..steps import (
    AddRecordIdStep,
    ReadPickleStep,
    ReplaceLargePropertiesStep,
    SplitAndMergeStep,
    WrapResultsStep,
)

__all__ = ["PredictCheckpointModel"]


class PredictCheckpointModel(Model):
    def __init__(
        self,
        base_model: Model,
        job_id: str,
        file_system: FileSystem,
        checkpoint_id: int,
        channel: Channel,
        loop: AbstractEventLoop,
    ) -> None:
        super().__init__()
        self._base_model = base_model
        self._job_id = job_id
        self._file_system = file_system
        self._checkpoint_id = checkpoint_id
        self._channel = channel
        self._loop = loop

    def _get_input_steps(
        self, input: Any, input_format: Optional[str], **kwargs: Any
    ) -> List[Step]:
        return [ReadPickleStep(input)]

    def _get_preprocessing_steps(
        self, input: Any, input_format: Optional[str], **kwargs: Any
    ) -> List[Step]:
        # do preprocessing as the encapsulated model would do
        return self._base_model._get_preprocessing_steps(input, input_format, **kwargs)

    def _get_postprocessing_steps(self, output_format: Optional[str], **kwargs: Any) -> List[Step]:
        # We would like to write the results in two different formats:
        #
        #                             /---> json -> send to results topic
        # predictions -> splitter ---|
        #                            \---> record_list -> save to disk
        #
        send_to_channel_steps = self._base_model._get_postprocessing_steps(
            output_format="json",
            # necessary for ChannelWriter:
            channel=self._channel,
            loop=self._loop,
            # necessary for other preprocessing steps:
            model=self._base_model,
            **kwargs,
        )

        # we have to insert additional steps before sending to channel
        send_to_channel_steps = [
            *send_to_channel_steps[:-1],
            # replace large properties with file references
            ReplaceLargePropertiesStep(
                self._base_model._get_config().get_dict(), self._file_system, self._job_id
            ),
            # add record ids
            AddRecordIdStep(self._job_id),
            # wrap results in ResultMessage
            WrapResultsStep(),
            # send to results topic
            send_to_channel_steps[-1],
        ]

        results_file = self._file_system.get_results_file_handle(
            self._job_id, self._checkpoint_id, "wb"
        )

        file_writing_steps = self._base_model._get_postprocessing_steps(
            output_format="pickle", output_file=results_file, **kwargs
        )

        return [SplitAndMergeStep(send_to_channel_steps, file_writing_steps)]

    def _predict_mols(self, mols: List[Mol], **kwargs: Any) -> Iterable[dict]:
        # do prediction as the encapsulated model would do
        return self._base_model._predict_mols(mols, **kwargs)

    def _get_config(self) -> Configuration:
        # return the configuration of the encapsulated model
        return self._base_model._get_config()

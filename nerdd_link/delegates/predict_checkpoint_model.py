from asyncio import AbstractEventLoop
from typing import IO, Any, Iterable, List, Optional

from nerdd_module import Model
from nerdd_module.config import Configuration
from nerdd_module.steps import Step
from rdkit.Chem import Mol

from ..channels import Channel
from ..steps import (
    AddRecordIdStep,
    ReadPickleStep,
    ReplaceLargePropertiesStep,
    SplitAndMergeStep,
    WrapResultsStep,
)
from ..storage import Storage

__all__ = ["PredictCheckpointModel"]


class PredictCheckpointModel(Model):
    def __init__(
        self,
        base_model: Model,
        job_id: str,
        storage: Storage,
        result_checkpoint_handle: IO,
        channel: Channel,
        loop: AbstractEventLoop,
    ) -> None:
        super().__init__()
        self._base_model = base_model
        self._job_id = job_id
        self._storage = storage
        self._result_checkpoint_handle = result_checkpoint_handle
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
                self._base_model._get_config().get_dict(), self._storage, self._job_id
            ),
            # add record ids
            AddRecordIdStep(self._job_id),
            # wrap results in ResultMessage
            WrapResultsStep(),
            # send to results topic
            send_to_channel_steps[-1],
        ]

        file_writing_steps = self._base_model._get_postprocessing_steps(
            output_format="pickle", output_file=self._result_checkpoint_handle, **kwargs
        )

        return [SplitAndMergeStep(send_to_channel_steps, file_writing_steps)]

    def _predict_mols(self, mols: List[Mol], **kwargs: Any) -> Iterable[dict]:
        # do prediction as the encapsulated model would do
        return self._base_model._predict_mols(mols, **kwargs)

    def _get_config(self) -> Configuration:
        # return the configuration of the encapsulated model
        return self._base_model._get_config()

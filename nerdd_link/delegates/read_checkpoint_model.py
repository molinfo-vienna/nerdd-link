from typing import Any, Iterable, List, Optional

from nerdd_module import Model, Step
from rdkit.Chem import Mol

from ..channels import Channel
from ..files import FileSystem
from .read_pickle_step import ReadPickleStep
from .split_and_merge_step import SplitAndMergeStep

__all__ = ["ReadCheckpointModel"]


class ReadCheckpointModel(Model):
    def __init__(
        self,
        base_model: Model,
        job_id: str,
        file_system: FileSystem,
        checkpoint_id: int,
        channel: Channel,
    ) -> None:
        super().__init__()
        self._base_model = base_model
        self._job_id = job_id
        self._file_system = file_system
        self._checkpoint_id = checkpoint_id
        self._channel = channel

    def _get_input_steps(
        self, input: Any, input_format: Optional[str], **kwargs: Any
    ) -> List[Step]:
        # we ignore the "input" argument and read from the checkpoint file
        checkpoints_file = self._file_system.get_checkpoint_file_handle(
            self._job_id, self._checkpoint_id, "rb"
        )
        return [ReadPickleStep(checkpoints_file)]

    def _get_preprocessing_steps(
        self, input: Any, input_format: Optional[str], **kwargs: Any
    ) -> List[Step]:
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
            model=self._base_model,
            job_id=self._job_id,
            checkpoint_id=self._checkpoint_id,
            channel=self._channel,
            **kwargs,
        )

        results_file = self._file_system.get_results_file_handle(
            self._job_id, self._checkpoint_id, "wb"
        )

        file_writing_steps = self._base_model._get_postprocessing_steps(
            output_format="pickle", output_file=results_file, **kwargs
        )

        return [SplitAndMergeStep(send_to_channel_steps, file_writing_steps)]

    def _predict_mols(self, mols: List[Mol], **kwargs: Any) -> Iterable[dict]:
        return self._base_model._predict_mols(mols, **kwargs)

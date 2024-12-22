import logging

from nerdd_module import Model, OutputStep
from stringcase import spinalcase

from ..channels import Channel
from ..delegates import ReadPickleStep
from ..files import FileSystem
from ..types import SerializationRequestMessage, SerializationResultMessage
from .action import Action

__all__ = ["SerializeJobAction"]


logger = logging.getLogger(__name__)


class SerializeJobAction(Action[SerializationRequestMessage]):
    def __init__(self, channel: Channel, model: Model, data_dir: str) -> None:
        super().__init__(channel.serialization_requests_topic(model))
        self._model = model
        self._file_system = FileSystem(data_dir)

    async def _process_message(self, message: SerializationRequestMessage) -> None:
        job_id = message.job_id
        params = message.params
        output_format = message.output_format
        logger.info(f"Write output for job {job_id} in format {output_format}")

        # remove specific parameter keys that could induce vulnerabilities
        params.pop("output_file", None)
        params.pop("output_format", None)

        output_file = self._file_system.get_output_file(job_id, output_format)

        # TODO: don't write the file if it exists

        read_pickle_step = ReadPickleStep(self._file_system.iter_results_file_handles(job_id))
        post_processing_steps = self._model._get_postprocessing_steps(
            output_format, output_file=output_file, **params
        )
        steps = [read_pickle_step, *post_processing_steps]
        output_step = steps[-1]
        assert isinstance(output_step, OutputStep), "The last step must be an OutputStep."

        # build the pipeline from the list of steps
        pipeline = None
        for t in steps:
            pipeline = t(pipeline)

        # run the pipeline by calling the get_result method of the last step
        output_step.get_result()

        await self.channel.serialization_results_topic().send(
            SerializationResultMessage(job_id=job_id, output_format=output_format)
        )

    def _get_group_name(self) -> str:
        model_name = spinalcase(self._model.__class__.__name__)
        return model_name

import json
import logging

from nerdd_module import Model

from ..channels import Channel
from ..files import FileSystem
from ..types import ModuleMessage, SystemMessage
from .action import Action

__all__ = ["RegisterModuleAction"]

logger = logging.getLogger(__name__)


class RegisterModuleAction(Action[SystemMessage]):
    def __init__(self, channel: Channel, model: Model, data_dir: str):
        super().__init__(channel.system_topic())
        # TODO: do this differently
        assert hasattr(model, "config")
        self._model = model
        self._file_system = FileSystem(data_dir)

    async def _process_message(self, message: SystemMessage) -> None:
        config = self._model.config
        logger.info(f"Registering module with id {config.id}")

        # save module as json to file
        module_file = self._file_system.get_module_file_path(config.id)
        json.dump(config.model_dump(), open(module_file, "w"))

        # send the initialization message
        await self.channel.modules_topic().send(ModuleMessage(id=config.id))

    def _get_group_name(self) -> str:
        model_id = self._model.config.id
        return f"register-module-{model_id}"

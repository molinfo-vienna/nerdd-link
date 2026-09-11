import json
import logging

from nerdd_module import Model

from ..channels import Channel
from ..storage import Storage
from ..types import ModuleMessage, SystemMessage
from .action import Action

__all__ = ["RegisterModuleAction"]

logger = logging.getLogger(__name__)


class RegisterModuleAction(Action[SystemMessage]):
    def __init__(self, channel: Channel, model: Model, storage: Storage) -> None:
        super().__init__(channel.system_topic())
        self._model = model
        self._storage = storage

    async def _process_message(self, message: SystemMessage) -> None:
        await self.register(force_announce=True)

    async def register(self, force_announce: bool = False) -> None:
        config = self._model.config
        new_config_json = config.model_dump()
        if self._storage.module_file_exists(config.id):
            with self._storage.get_module_file_handle(config.id, "r") as f:
                old_config_json = json.load(f)
        else:
            old_config_json = None

        config_changed = new_config_json != old_config_json
        if config_changed:
            with self._storage.get_module_file_handle(config.id, "w") as f:
                json.dump(new_config_json, f)

        # Announce the module after its configuration has been persisted.
        if config_changed or force_announce:
            logger.info("Registering module with id %s", config.id)
            await self.channel.modules_topic().send(ModuleMessage(id=config.id))

    def _get_group_name(self) -> str:
        model_id = self._model.config.id
        return f"register-module-{model_id}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self._model!r}, storage={self._storage!r})"

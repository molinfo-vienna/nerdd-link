import logging

from nerdd_module import Model
from stringcase import spinalcase

from ..channels import Channel
from ..types import ModuleMessage, SystemMessage
from .action import Action

__all__ = ["RegisterModuleAction"]

logger = logging.getLogger(__name__)


class RegisterModuleAction(Action[SystemMessage]):
    def __init__(self, channel: Channel, model: Model):
        super().__init__(channel.system_topic())
        # TODO: do this differently
        assert hasattr(model, "get_config")
        self._model = model

    async def _process_message(self, message: SystemMessage) -> None:
        # send the initialization message
        config = self._model.get_config()
        logger.info(f"Send registration message for module {config.name}")
        await self.channel.modules_topic().send(ModuleMessage(**config.model_dump()))

    def _get_group_name(self) -> str:
        model_name = spinalcase(self._model.__class__.__name__)
        return model_name

import logging

from nerdd_module import Model

from ..channels import Channel
from ..types import ModuleMessage, SystemMessage
from .action import Action

__all__ = ["RegisterModuleAction"]

logger = logging.getLogger(__name__)


class RegisterModuleAction(Action[SystemMessage]):
    def __init__(self, channel: Channel, model: Model):
        super().__init__(channel.system_topic())
        self._model = model

    def _process_message(self, message: SystemMessage) -> None:
        # send the initialization message
        config = self._model.get_config()
        self.channel.modules_topic().send(ModuleMessage(**config))
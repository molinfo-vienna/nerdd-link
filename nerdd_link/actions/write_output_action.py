from nerdd_module import Model
from stringcase import spinalcase

from ..channels import Channel
from ..types import SystemMessage
from .action import Action

__all__ = ["WriteOutputAction"]


class WriteOutputAction(Action[SystemMessage]):
    def __init__(self, channel: Channel, model: Model):
        super().__init__(channel.system_topic())
        self._model = model

    async def _process_message(self, message: SystemMessage) -> None:
        pass

    def _get_group_name(self) -> str:
        model_name = spinalcase(self._model.__class__.__name__)
        return model_name

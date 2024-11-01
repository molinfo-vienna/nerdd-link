from ..channels import Channel
from ..types import SystemMessage
from .action import Action

__all__ = ["WriteOutputAction"]


class WriteOutputAction(Action[SystemMessage]):
    def __init__(self, channel: Channel):
        super().__init__(channel.system_topic())

    def _process_message(self, message: SystemMessage) -> None:
        return super()._process_message(message)

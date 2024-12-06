import logging

import rich_click as click

from ..channels import KafkaChannel
from ..types import SystemMessage
from ..utils import async_to_sync

__all__ = ["initialize_system"]

logger = logging.getLogger(__name__)


@click.command(context_settings={"show_default": True})
@click.option(
    "--channel",
    type=click.Choice(["kafka"], case_sensitive=False),
    default="kafka",
    help="Channel to use for communication with the model.",
)
@click.option("--broker-url", default="localhost:9092", help="Kafka broker to connect to.")
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(["debug", "info", "warning", "error", "critical"], case_sensitive=False),
    help="The logging level.",
)
@async_to_sync
async def initialize_system(
    # communication options
    channel: str,
    broker_url: str,
    # log level
    log_level: str,
) -> None:
    logging.basicConfig(level=log_level.upper())

    channel_instance = None
    if channel == "kafka":
        channel_instance = KafkaChannel(broker_url)
    else:
        raise ValueError(f"Channel {channel} not supported.")

    logging.info("Sending the system initialization message...")
    await channel_instance.system_topic().send(SystemMessage())

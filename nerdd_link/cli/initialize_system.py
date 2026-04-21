import logging
from typing import Optional

import rich_click as click

from ..channels import Channel
from ..types import SystemMessage
from ..utils import async_to_sync

__all__ = ["initialize_system"]

logger = logging.getLogger(__name__)


@click.command(context_settings={"show_default": True})
@click.option(
    "--channel",
    type=click.Choice(Channel.get_channel_names(), case_sensitive=False),
    default="kafka",
    help="Channel to use for communication with the model.",
)
@click.option(
    "--broker-url",
    default="localhost:9092",
    help=(
        "Broker url to connect to (e.g. localhost:9092 for Kafka or "
        "rabbitmq://guest:guest@localhost:5552/ for RabbitMQ Streams)."
    ),
)
@click.option(
    "--broker-username",
    default=None,
    help="Broker username to use for authenticated connections.",
)
@click.option(
    "--broker-password",
    default=None,
    help="Broker password to use for authenticated connections.",
)
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
    broker_username: Optional[str],
    broker_password: Optional[str],
    # log level
    log_level: str,
) -> None:
    logging.basicConfig(level=log_level.upper())

    channel_instance = Channel.create_channel(
        channel,
        broker_url=broker_url,
        broker_username=broker_username,
        broker_password=broker_password,
    )

    async with channel_instance:
        logger.info("Initializing system...")
        await channel_instance.system_topic().send(SystemMessage())
        logger.info("System initialized.")

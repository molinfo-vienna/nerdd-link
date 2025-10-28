import asyncio
import logging
from typing import List, Optional

import rich_click as click

from ..actions import Action, SerializeJobAction
from ..channels import Channel
from ..utils import async_to_sync

logger = logging.getLogger(__name__)


async def _run_serialization_server(channel: Channel, data_dir: str) -> None:
    await channel.start()

    serialize_job = SerializeJobAction(
        channel=channel,
        data_dir=data_dir,
    )

    actions: List[Action] = [serialize_job]

    tasks = [asyncio.create_task(action.run()) for action in actions]
    try:
        for task in tasks:
            logging.info(f"Running action {task}")
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        await channel.stop()


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
    "--data-dir",
    default="sources",
    help="Directory containing structure files associated with the incoming jobs.",
)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(["debug", "info", "warning", "error", "critical"], case_sensitive=False),
    help="The logging level.",
)
@async_to_sync
async def run_serialization_server(
    # communication options
    channel: str,
    broker_url: str,
    broker_username: Optional[str],
    broker_password: Optional[str],
    # options
    data_dir: str,
    # log level
    log_level: str,
) -> None:
    logging.basicConfig(level=log_level.upper())

    channel_kwargs = {"broker_url": broker_url}
    if broker_username is not None:
        channel_kwargs["broker_username"] = broker_username
    if broker_password is not None:
        channel_kwargs["broker_password"] = broker_password

    channel_instance = Channel.create_channel(channel, **channel_kwargs)

    await _run_serialization_server(
        channel=channel_instance,
        data_dir=data_dir,
    )

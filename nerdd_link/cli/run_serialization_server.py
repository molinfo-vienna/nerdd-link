import asyncio
import logging
from typing import List

import rich_click as click

from ..actions import Action, SerializeJobAction
from ..channels import Channel
from ..utils import async_to_sync

__all__ = ["run_serialization_server"]

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
    # options
    data_dir: str,
    # log level
    log_level: str,
) -> None:
    logging.basicConfig(level=log_level.upper())

    channel_instance = Channel.create_channel(channel, broker_url=broker_url)

    await channel_instance.start()

    serialize_job = SerializeJobAction(
        channel=channel_instance,
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

        await channel_instance.stop()

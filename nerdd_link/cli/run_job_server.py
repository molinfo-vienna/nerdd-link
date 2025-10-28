import asyncio
import logging
from typing import Optional

import rich_click as click

from ..actions import ProcessJobsAction
from ..channels import Channel
from ..utils import async_to_sync

__all__ = ["run_job_server"]

logger = logging.getLogger(__name__)


async def _run_job_server(
    channel: Channel,
    num_test_entries: int,
    ratio_valid_entries: float,
    maximum_depth: int,
    # reading options for readers
    max_num_lines_mol_block: int,
    data_dir: str,
) -> None:
    await channel.start()

    action = ProcessJobsAction(
        channel,
        num_test_entries,
        ratio_valid_entries,
        maximum_depth,
        max_num_lines_mol_block,
        data_dir,
    )

    task = asyncio.create_task(action.run())
    try:
        logging.info(f"Running action {action}")
        await task
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        task.cancel()
        await task

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
    "--num-test-entries",
    default=10,
    help="Number of entries to use for guessing the format of the input file.",
)
@click.option(
    "--ratio-valid-entries",
    default=0.6,
    help="Ratio of valid entries to use for guessing the format of the input file.",
)
@click.option(
    "--maximum-depth",
    default=50,
    help="Maximum level of nesting allowed for reading files.",
)
@click.option(
    "--max-num-lines-mol-block",
    default=10_000,
    help="Maximum number of lines in a molecule block before giving up parsing.",
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
async def run_job_server(
    # communication options
    channel: str,
    broker_url: str,
    broker_username: Optional[str],
    broker_password: Optional[str],
    # reading options for DepthFirstExplorer
    num_test_entries: int,
    ratio_valid_entries: float,
    maximum_depth: int,
    # reading options for readers
    max_num_lines_mol_block: int,
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

    await _run_job_server(
        channel=channel_instance,
        num_test_entries=num_test_entries,
        ratio_valid_entries=ratio_valid_entries,
        maximum_depth=maximum_depth,
        max_num_lines_mol_block=max_num_lines_mol_block,
        data_dir=data_dir,
    )

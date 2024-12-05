import asyncio
import logging

import rich_click as click

from ..actions import ProcessJobsAction
from ..channels import KafkaChannel
from ..utils import async_to_sync

__all__ = ["run_job_server"]

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
    "--max-num-molecules",
    default=10_000,
    help="Maximum number of molecules in a job to process.",
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
    "--checkpoint-size",
    default=200,
    help="Number of input entries that are put in a checkpoint file.",
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
    # reading options for DepthFirstExplorer
    max_num_molecules: int,
    num_test_entries: int,
    ratio_valid_entries: float,
    maximum_depth: int,
    # reading options for readers
    max_num_lines_mol_block: int,
    data_dir: str,
    checkpoint_size: int,
    # log level
    log_level: str,
) -> None:
    logging.basicConfig(level=log_level.upper())

    channel_instance = None
    if channel == "kafka":
        channel_instance = KafkaChannel(broker_url)
    else:
        raise ValueError(f"Channel {channel} not supported.")

    action = ProcessJobsAction(
        channel_instance,
        checkpoint_size,
        max_num_molecules,
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

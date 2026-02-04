import logging
from typing import List, Optional

import rich_click as click

from ..actions import Action, SerializeJobAction, supervise_actions
from ..channels import Channel
from ..storage import Storage
from ..utils import async_to_sync
from .get_storage import get_storage
from .validate_storage_options import validate_storage_options

logger = logging.getLogger(__name__)


async def _run_serialization_server(channel: Channel, storage: Storage) -> None:
    try:
        async with channel:
            serialize_job = SerializeJobAction(
                channel=channel,
                storage=storage,
            )

            actions: List[Action] = [serialize_job]

            await supervise_actions(actions)
    except KeyboardInterrupt:
        # we catch KeyboardInterrupt so it is not displayed to the user
        pass
    finally:
        logger.info("Server shut down successfully")


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
    default=None,
    help="Directory containing structure files associated with the incoming jobs.",
)
@click.option(
    "--s3-url",
    default=None,
    help="S3 endpoint URL.",
)
@click.option(
    "--s3-bucket",
    default=None,
    help="S3 bucket name.",
)
@click.option(
    "--s3-username",
    default=None,
    help="S3 username.",
)
@click.option(
    "--s3-password",
    default=None,
    help="S3 password.",
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
    data_dir: Optional[str],
    s3_url: Optional[str],
    s3_bucket: Optional[str],
    s3_username: Optional[str],
    s3_password: Optional[str],
    # log level
    log_level: str,
) -> None:
    validate_storage_options(data_dir, s3_url, s3_bucket, s3_username, s3_password)
    logging.basicConfig(level=log_level.upper())

    channel_kwargs = {"broker_url": broker_url}
    if broker_username is not None:
        channel_kwargs["broker_username"] = broker_username
    if broker_password is not None:
        channel_kwargs["broker_password"] = broker_password

    channel_instance = Channel.create_channel(channel, **channel_kwargs)
    storage = get_storage(data_dir, s3_url, s3_bucket, s3_username, s3_password)

    await _run_serialization_server(
        channel=channel_instance,
        storage=storage,
    )

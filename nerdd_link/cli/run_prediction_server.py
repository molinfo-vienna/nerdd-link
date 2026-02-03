import asyncio
import json
import logging
import signal
from importlib import import_module
from typing import Any, List, Optional

import rich_click as click
from nerdd_module import Model

from ..actions import Action, PredictCheckpointsAction, supervise_actions
from ..channels import Channel
from ..storage import Storage
from ..types import ModuleMessage
from ..utils import async_to_sync
from .get_storage import get_storage

logger = logging.getLogger(__name__)


async def _run_prediction_server(model: Model, channel: Channel, storage: Storage) -> None:
    # enable graceful shutdown on SIGTERM
    loop = asyncio.get_running_loop()

    def handle_termination_signal(*args: Any) -> None:
        logger.info("Received termination signal, shutting down...")
        asyncio.run_coroutine_threadsafe(channel.stop(), loop)

    loop.add_signal_handler(signal.SIGTERM, handle_termination_signal)

    try:
        async with channel:
            #
            # register the module
            #
            # compare old json with new one, only write if changed
            new_config_json = model.config.model_dump()
            if storage.module_file_exists(model.config.id):
                with storage.get_module_file_handle(model.config.id, "r") as f:
                    old_config_json = json.load(f)
            else:
                old_config_json = None
            if new_config_json != old_config_json:
                logger.info(f"Registering module {model.config.id}")
                with storage.get_module_file_handle(model.config.id, "w") as f:
                    json.dump(new_config_json, f)
                await channel.modules_topic().send(ModuleMessage(id=model.config.id))

            #
            # run prediction
            #
            predict_checkpoints = PredictCheckpointsAction(
                channel=channel,
                model=model,
                storage=storage,
            )

            # run actions in parallel
            actions: List[Action] = [predict_checkpoints]

            await supervise_actions(actions)
    except KeyboardInterrupt:
        # we catch KeyboardInterrupt so it is not displayed to the user
        pass
    finally:
        logger.info("Server shut down successfully")


@click.command(context_settings={"show_default": True})
@click.argument("model-name")
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
async def run_prediction_server(
    # communication options
    channel: str,
    broker_url: str,
    broker_username: Optional[str],
    broker_password: Optional[str],
    # options
    model_name: str,
    data_dir: str,
    s3_bucket: Optional[str],
    s3_username: Optional[str],
    s3_password: Optional[str],
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
    storage = get_storage(data_dir, s3_bucket, s3_username, s3_password)

    # import the model class
    package_name, class_name = model_name.rsplit(".", 1)
    package = import_module(package_name)
    Model = getattr(package, class_name)
    model = Model()

    await _run_prediction_server(
        model=model,
        channel=channel_instance,
        storage=storage,
    )

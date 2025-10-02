import asyncio
import json
import logging
import os
import signal
from importlib import import_module
from typing import Any, List

import rich_click as click
from nerdd_module import Model

from ..actions import Action, PredictCheckpointsAction
from ..channels import Channel
from ..files import FileSystem
from ..types import ModuleMessage
from ..utils import async_to_sync

logger = logging.getLogger(__name__)


async def _run_prediction_server(model: Model, channel: Channel, data_dir: str) -> None:
    await channel.start()

    # enable graceful shutdown on SIGTERM
    loop = asyncio.get_running_loop()

    def handle_termination_signal(*args: Any) -> None:
        logger.info("Received termination signal, shutting down...")
        asyncio.run_coroutine_threadsafe(channel.stop(), loop)

    loop.add_signal_handler(signal.SIGTERM, handle_termination_signal)

    #
    # register the module
    #
    file_system = FileSystem(data_dir)
    module_file_path = file_system.get_module_file_path(model.config.id)

    # compare old json with new one, only write if changed
    new_config_json = model.config.model_dump()
    if os.path.exists(module_file_path):
        old_config_json = json.load(open(module_file_path, "r"))
    else:
        old_config_json = None
    if new_config_json != old_config_json:
        logger.info(f"Registering module {model.config.id}")
        json.dump(new_config_json, open(module_file_path, "w"))
        await channel.modules_topic().send(ModuleMessage(id=model.config.id))

    #
    # run prediction
    #
    predict_checkpoints = PredictCheckpointsAction(
        channel=channel,
        model=model,
        data_dir=data_dir,
    )

    # enable running multiple actions in the future
    actions: List[Action] = [predict_checkpoints]

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

    logger.info("Server shut down successfully")


@click.command(context_settings={"show_default": True})
@click.argument("model-name")
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
async def run_prediction_server(
    # communication options
    channel: str,
    broker_url: str,
    # options
    model_name: str,
    data_dir: str,
    # log level
    log_level: str,
) -> None:
    logging.basicConfig(level=log_level.upper())

    channel_instance = Channel.create_channel(channel, broker_url=broker_url)

    # import the model class
    package_name, class_name = model_name.rsplit(".", 1)
    package = import_module(package_name)
    Model = getattr(package, class_name)
    model = Model()

    await _run_prediction_server(
        model=model,
        channel=channel_instance,
        data_dir=data_dir,
    )

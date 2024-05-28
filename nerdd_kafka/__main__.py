import logging
from importlib import import_module

import rich_click as click

from .kafka_server import KafkaServer

logger = logging.getLogger(__name__)


@click.command(context_settings={"show_default": True})
@click.argument(
    "model-name",
)
@click.option(
    "--broker-url", default="localhost:9092", help="Kafka broker to connect to."
)
@click.option(
    "--batch-size",
    default=100,
    help="The batch size that are efficiently processable by this model.",
)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
    help="The logging level.",
)
def main(
    model_name: str,
    broker_url: str,
    batch_size: int,
    log_level: str,
):
    logging.basicConfig(level=log_level.upper())

    package_name, class_name = model_name.rsplit(".", 1)

    package = import_module(package_name)
    Model = getattr(package, class_name)
    model = Model()

    config = model.get_config().get_dict()
    name = config.get("name", class_name)

    # create job_type identifier from name by
    # * converting to lowercase and
    # * removing all characters except dash and alphanumeric characters
    job_type = name.lower()
    job_type = "".join([c for c in job_type if str.isalnum(c) or c == "-"])

    # input topic is the job type with "-inputs" appended
    input_topic = f"{job_type}-inputs"

    logger.info(
        f"Running server using model {model_name} with job type {job_type} and input "
        f"topic {input_topic}. Using a batch size of {batch_size}. Connecting to "
        f"broker {broker_url}."
    )

    KafkaServer().start(
        model,
        job_type,
        broker_url,
        input_topic,
        batch_size=batch_size,
    )

import logging
from importlib import import_module

import rich_click as click
from stringcase import spinalcase

from .kafka_server import run_server

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
    "--job-type",
    default=None,
    help=(
        "The job type this module accepts. If not specified, it will be inferred "
        "from the model name."
    ),
)
@click.option(
    "--input-topic",
    default=None,
    help="The Kafka topic this server will obtain its tasks from.",
)
@click.option(
    "--log-level",
    default="warning",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
    help="The logging level.",
)
def main(
    model_name: str,
    broker_url: str,
    job_type: str,
    input_topic: str,
    batch_size: int,
    log_level: str,
):
    logging.basicConfig(level=log_level.upper())

    # model name
    package_name, class_name = model_name.rsplit(".", 1)

    # job type
    if job_type is None:
        if class_name.endswith("Model"):
            # remove the "Model" suffix and convert to spinal case
            # e.g. SkinDoctorModel -> skin-doctor
            job_type = spinalcase(class_name[: -len("Model")])
        else:
            job_type = spinalcase(class_name)

    # input topic
    if input_topic is None:
        input_topic = f"{job_type}-inputs"

    package = import_module(package_name)
    Model = getattr(package, class_name)
    model = Model()

    logger.info(
        f"Running server using model {model_name} on {job_type} with input "
        f"topic {input_topic}. Using a batch size of {batch_size}. Connecting to "
        f"broker {broker_url}."
    )

    run_server(
        model,
        job_type,
        broker_url,
        input_topic,
        batch_size=batch_size,
    )

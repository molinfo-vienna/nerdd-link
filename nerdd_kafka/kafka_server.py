import json
import logging
from collections import defaultdict

from nerdd_module.abstract_model import AbstractModel
from rdkit.Chem import MolToSmiles

from .serialization import ComplexJsonEncoder

logger = logging.getLogger(__name__)

__all__ = ["run_server"]


def run_server(
    model: AbstractModel,
    job_type: str,
    broker: str,
    input_topic: str,
    batch_size: int = 100,
):
    # we want to be able to mock KafkaConsumer and KafkaProducer in tests
    # --> only import them here
    from kafka import KafkaConsumer, KafkaProducer

    logger.info("Start Kafka Consumer")
    consumer = KafkaConsumer(
        input_topic,
        bootstrap_servers=[broker],
        api_version=(3, 3, 1),
        auto_offset_reset="earliest",
        group_id=f"{job_type}-consumer-group",
        enable_auto_commit=False,
        max_poll_records=batch_size,
    )

    producer = KafkaProducer(
        bootstrap_servers=[broker],
        api_version=(3, 3, 1),
        max_request_size=10 * 1024 * 1024,  # 10 MB
    )

    #
    # send the initialization message
    #
    config = model.get_config()

    config_dict = config.get_dict()

    assert "name" in config_dict, "name is missing in config"

    init_message = {
        "type": "init",
        "name": config_dict["name"],
        "config": config_dict,
    }

    producer.send("modules", json.dumps(init_message).encode("utf-8")).get()

    #
    # identify the type of this module
    #
    module_type = config.get_module_type()

    #
    # check which columns of the predictions should be included in messages
    # specifically, atom or derivative properties are sent in separate messages
    #
    default_molecule_columns = [
        "job_id",
        "job_type",
        "mol_id",
        "input_mol",
        "input",
        "input_type",
        "name",
        "input_smiles",
        "preprocessed_smiles",
        "errors",
    ]

    default_atom_columns = ["job_id", "job_type", "mol_id", "atom_id"]

    default_derivative_columns = ["job_id", "job_type", "mol_id", "derivative_id"]

    molecular_property_columns = (
        default_molecule_columns + config.molecular_property_columns()
    )
    atom_property_columns = default_atom_columns + config.atom_property_columns()
    derivative_property_columns = (
        default_derivative_columns + config.derivative_property_columns()
    )

    #
    # receive and process messages
    #
    while True:
        # we use polling (instead of iterating through the consumer messages) to
        # be able to process batches of messages at once (ML models love batches)
        messages = consumer.poll(timeout_ms=1000)

        if messages:
            logger.info(f"Received {len(messages)} messages")

            # A model can only process batches with the same model parameters (e.g.
            # CYPstrate needs a constant prediction_mode for all molecules in a batch).
            # --> partition messages into buckets by job-id and input-type
            try:
                job_messages = defaultdict(list)
                for _, message_list in messages.items():
                    for message in message_list:
                        message_obj = json.loads(message.value)
                        job_id = message_obj["job_id"]
                        input_type = message_obj["input_type"]
                        key = f"{job_id}-{input_type}"
                        job_messages[key].append(message_obj)
            except Exception as e:
                logger.error("Error partitioning messages", exc_info=e)
                continue

            for _, message_list in job_messages.items():
                try:
                    first_message = message_list[0]
                    assert "job_id" in first_message, "job_id is missing"
                    assert "job_type" in first_message, "job_type is missing"
                    assert "input_type" in first_message, "input_type is missing"
                    assert (
                        first_message["job_type"] == job_type
                    ), f"job_type is not {job_type}"

                    job_id = first_message["job_id"]
                    input_type = first_message["input_type"]
                    params = first_message["params"]

                    logger.info(
                        f"Processing part of job {job_id} with a batch size of "
                        f"{len(message_list)} molecules"
                    )

                    logger.info(f"Predicting molecules given as {input_type}")
                    results = model.predict(
                        [message["raw_input"] for message in message_list],
                        input_type=input_type,
                        **params,
                    )

                    logger.info(f"Produced results: {len(results)}")

                    results["job_id"] = job_id
                    results["job_type"] = job_type

                    # map mol_id (ranging from 0 to n) to the original mol_id provided
                    # in the field mol_id of each message in message_list
                    results["mol_id"] = [
                        message_list[mol_id]["mol_id"] for mol_id in results["mol_id"]
                    ]

                    def _to_smiles(mol):
                        if mol is None:
                            return None
                        else:
                            return MolToSmiles(mol)

                    results["input_smiles"] = results.input_mol.map(_to_smiles)
                    results["preprocessed_smiles"] = results.preprocessed_mol.map(
                        _to_smiles
                    )

                    #
                    # send results to output topic
                    #

                    # send molecule properties
                    results_molecule = (
                        results[molecular_property_columns]
                        .drop_duplicates(subset="mol_id")
                        .to_dict("records")
                    )
                    for entry in results_molecule:
                        producer.send(
                            "results",
                            json.dumps(entry, cls=ComplexJsonEncoder).encode("utf-8"),
                        ).get()

                    # optionally send atom properties
                    if module_type == "atom_property_predictor":
                        results_atom = results[results.atom_id.notnull()][
                            atom_property_columns
                        ].to_dict("records")
                        for entry in results_atom:
                            producer.send(
                                "results",
                                json.dumps(entry, cls=ComplexJsonEncoder).encode(
                                    "utf-8"
                                ),
                            ).get()

                    # optionally send derivative properties
                    if module_type == "derivative_property_predictor":
                        results_derivative = results[results.derivative_id.notnull()][
                            derivative_property_columns
                        ].to_dict("records")
                        for entry in results_derivative:
                            producer.send(
                                "results",
                                json.dumps(entry, cls=ComplexJsonEncoder).encode(
                                    "utf-8"
                                ),
                            ).get()
                except Exception as e:
                    logger.error(f"Error processing input: {message_list}", exc_info=e)

            # commit the message offsets we have processed
            consumer.commit()

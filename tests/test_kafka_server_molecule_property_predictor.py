import pytest
from pytest_bdd import given, parsers, scenario, then, when


@scenario(
    "features/kafka_server.feature",
    "Processing input molecules using a molecule property predictor",
)
def test_kafka_server_processing():
    pass


@given("the number of expected results", target_fixture="expected_number_of_results")
def expected_number_of_results(input_batches):
    return sum(len(batch) for batch in input_batches)

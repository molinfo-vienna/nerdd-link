import json
import time

from pytest_bdd import given, scenario, then


@scenario("features/kafka_server.feature", "Start a server with a model")
def test_kafka_server_initialization():
    pass


@given("no input messages", target_fixture="input_batches")
def input_batches():
    return []


@then("the server sends a configuration message")
def check_config_message(predictor, mocked_kafka_producer):
    send_method = mocked_kafka_producer.return_value.send

    # server might not have started yet
    # --> try multiple times
    for _ in range(5):
        if send_method.call_count == 0:
            time.sleep(1)
            continue

        call_args = send_method.call_args_list[0]
        topic, message = call_args[0]

        assert topic == "modules"

        obj = json.loads(message.decode("utf-8"))

        assert obj["type"] == "init"
        assert obj["config"] == predictor.get_config().get_dict()

        return

    assert False, "No config message sent"

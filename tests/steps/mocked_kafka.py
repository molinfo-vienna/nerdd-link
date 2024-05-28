import json
import time
from threading import Thread

from kafka.consumer.fetcher import ConsumerRecord
from pytest_bdd import given, then, when


@given("a mocked kafka consumer", target_fixture="mocked_kafka_consumer")
def mocked_kafka_consumer(mocker, input_batches):
    topic_name = "dummy_inputs"

    mocked = mocker.patch("kafka.KafkaConsumer", autospec=True)

    # mocker.patch mocks all methods of the KafkaConsumer class, but we have to
    # replace the function "poll" explicitly, because it should do something special:
    # (1) return the fake messages from the input_messages fixture and
    # (2) wait indefinitely if there are no messages
    # --> the latter has to be implemented with a so called "side effect"

    # we keep track of the current fake batch with a global variable:
    current_batch = 0

    # this function serves the messages from the input_messages fixture
    # and waits indefinitely if there are no messages
    def serve_and_wait_indefinitely(*args, **kwargs):
        nonlocal current_batch

        # serve all messages we would like to have processed
        for i, batch in enumerate(input_batches):
            if i != current_batch:
                continue

            current_batch += 1

            records = [
                ConsumerRecord(
                    topic_name,
                    "topic_partition_1",
                    current_batch,
                    timestamp=None,
                    timestamp_type=None,
                    key=None,
                    value=json.dumps(row),
                    headers=None,
                    checksum=None,
                    serialized_key_size=0,
                    serialized_value_size=len(json.dumps(row)),
                    serialized_header_size=0,
                )
                for row in batch
            ]

            # return messages like a real KafkaConsumer would do
            # should be a dict mapping
            # * from topic_partition (of type str)
            # * to records (of type List[ConsumerRecord])
            return dict(topic_partition_1=records)

        time.sleep(1)
        return None

    # note: the variable mocked holds the KafkaConsumer *class* and return_value is the
    # KafkaConsumer *instance*
    mocked.return_value.poll.side_effect = serve_and_wait_indefinitely

    return mocked


@given("a mocked kafka producer", target_fixture="mocked_kafka_producer")
def mocked_kafka_producer(mocker):
    return mocker.patch("kafka.KafkaProducer", autospec=True)


@given("a kafka server initialized with the model", target_fixture="kafka_server")
def kafka_server(mocker, predictor, mocked_kafka_consumer, mocked_kafka_producer):
    class ServerThread(Thread):
        def __init__(self):
            super().__init__()
            # Importing nerdd_kafka at the top of the file would already import
            # the KafkaConsumer and KafkaProducer classes. However, we want to mock
            # these classes in the test, so we have to import them after the mocks
            # have been set up! That is why we import the KafkaServer class here.
            from nerdd_kafka import KafkaServer

            self.server = KafkaServer()

        def run(self):
            self.server.start(predictor, "dummy", "localhost", "dummy_inputs", 100)

        def stop(self):
            self.server.stop()

    server_thread = ServerThread()
    server_thread.start()
    return server_thread


@then("the server is shut down")
def check_server_is_shut_down(kafka_server):
    time.sleep(5)
    kafka_server.stop()
    kafka_server.join()


@when(
    "the server responds",
    target_fixture="prediction_response",
)
def prediction_response(expected_number_of_results, mocked_kafka_producer):
    results = []

    # server might not have started sending yet
    # --> try multiple times
    for _ in range(5):
        for call_args in mocked_kafka_producer.return_value.send.call_args_list:
            topic, message = call_args[0]

            if topic == "results":
                results.append(json.loads(message))

            if len(results) == expected_number_of_results:
                break

        time.sleep(1)

    if len(results) == 0:
        assert False, "No message was sent to the results topic"

    return results

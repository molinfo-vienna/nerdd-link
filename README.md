<h1 align="center">
    nerdd-link
</h1>

<hr/>

<div align="center">

![PyPI version](https://img.shields.io/pypi/v/nerdd-link)
![Python versions](https://img.shields.io/pypi/pyversions/nerdd-link)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?logo=apachekafka&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?logo=rabbitmq&logoColor=white)
![License](https://img.shields.io/github/license/molinfo-vienna/nerdd-link)

</div>

<div align="center">
<a href="https://github.com/molinfo-vienna/nerdd-module">📦 nerdd-module</a>
•
<a href="https://github.com/molinfo-vienna/nerdd">⚙️ Infrastructure</a>
•
<a href="https://nerdd.univie.ac.at">🌐 NERDD website</a>
</div>

<br/>

**nerdd-link** wraps a [NERDD module](https://github.com/molinfo-vienna/nerdd-module) in a service
that is able to communicate with a message broker to receive prediction jobs and return their
results. It also provides supporting services for running NERDD in a cluster.


## Installation

```bash
pip install -U nerdd-link
```

## Services

### Prediction service

The prediction service wraps a NERDD module, consumes prediction checkpoints, and returns the
results. The model is specified as the fully qualified name of its Python class. For example, the
following command runs `ExampleModel` with local storage:

```bash
nerdd_prediction_server example_module.ExampleModel \
    --channel kafka \
    --broker-url localhost:9092 \
    --broker-username nerdd \
    --broker-password secret \
    --log-level info \
    --data-dir ./data
    # or:
    # --s3-url http://localhost:9000 \
    # --s3-bucket nerdd \
    # --s3-access-key-id example-access-key \
    # --s3-secret-access-key example-secret-key
```

### Job service

The job service reads and validates molecular inputs and splits jobs into checkpoints.

```bash
nerdd_job_server \
    --channel kafka \
    --broker-url localhost:9092 \
    --broker-username nerdd \
    --broker-password secret \
    --num-test-entries 10 \
    --ratio-valid-entries 0.6 \
    --maximum-depth 50 \
    --max-num-lines-mol-block 10000 \
    --log-level info \
    --data-dir ./data
    # or:
    # --s3-url http://localhost:9000 \
    # --s3-bucket nerdd \
    # --s3-access-key-id example-access-key \
    # --s3-secret-access-key example-secret-key
```

### Serialization service

The serialization service combines completed prediction checkpoints and writes the results in the
requested output format.

```bash
nerdd_serialization_server \
    --channel kafka \
    --broker-url localhost:9092 \
    --broker-username nerdd \
    --broker-password secret \
    --log-level info \
    --data-dir ./data
    # or:
    # --s3-url http://localhost:9000 \
    # --s3-bucket nerdd \
    # --s3-access-key-id example-access-key \
    # --s3-secret-access-key example-secret-key
```

## Actions

An `Action` is a long-running worker that consumes messages from one `Topic`, processes them, and
sends messages to other topics. Services use `supervise_actions()` to run one or more actions
concurrently. If an action fails or finishes unexpectedly while its channel is still running, the
supervisor restarts it.

### Existing actions

- `ProcessJobsAction` consumes job messages, reads and validates their molecular inputs, writes
  input checkpoints, and publishes a message for each checkpoint.
- `PredictCheckpointsAction` consumes checkpoint messages for a NERDD module, runs the model,
  stores result checkpoints, and publishes prediction results.
- `SerializeJobAction` consumes serialization requests, combines the stored result
  checkpoints, and writes the requested output format.
- `RegisterModuleAction` stores a module's configuration and announces the module. It repeats
  the announcement when it receives a system initialization message.

### Adding an action

Create an action by subclassing `Action` with the type of message it consumes. Its constructor must
pass the input topic to `super().__init__()`. The default batch size is one and can be changed with
the `batch_size` argument.

The following hooks are available; optional hooks are marked accordingly:

- `_process_message(message)`: Processes messages individually. Alternatively, override
  `_process_messages(messages)` to process an entire batch.
- (optional) `_process_tombstone(tombstone)`: Handles one tombstone message.
- (optional) `_process_tombstones(tombstones)`: Handles all tombstones in a batch.
- (optional) `_get_group_name()`: Returns the consumer-group name. By default, the action's class
  name is converted to spinal case.

Regular messages in a batch are processed before its tombstones. The default batch hooks invoke
the corresponding single-message hook sequentially. Exceptions should be allowed to propagate so
that `supervise_actions()` can restart the action.

```python
from nerdd_link import Action, Channel, JobMessage, Tombstone


class ExampleAction(Action[JobMessage]):
    def __init__(self, channel: Channel) -> None:
        super().__init__(channel.jobs_topic(), batch_size=10)

    async def _process_message(self, message: JobMessage) -> None:
        # Process one job message.
        ...

    async def _process_tombstone(self, tombstone: Tombstone[JobMessage]) -> None:
        # Remove data associated with the deleted job.
        ...

    def _get_group_name(self) -> str:
        return "example-action"
```


## Message brokers

nerdd-link uses channels to communicate with message brokers. The following channel
implementations are available:

- `ConfluentKafkaChannel` (`--channel confluent_kafka`) connects to Kafka using the
  `confluent-kafka` client.
- `AioKafkaChannel` (`--channel aio_kafka`) connects to Kafka using the asynchronous `aiokafka`
  client.
- `KafkaChannel` (`--channel kafka`) is a synonym for `ConfluentKafkaChannel`, which is the
  recommended kafka channel implementation at the moment.
- `RabbitmqStreamsChannel` (`--channel rabbitmq_streams`) connects to RabbitMQ Streams using
  the `rstream` client.
- `MemoryChannel` (`--channel memory`) keeps messages in memory and is intended for testing
  without an external broker.

### Adding a channel

Support for another message broker can be added by subclassing `Channel`. A channel implementation
must call `super().__init__()` and implement the methods below unless they are marked as optional:

- `_iter_messages(topic, consumer_group, batch_size)`: Receives messages and yields batches of
  `(key, value)` tuples. A `None` value represents a tombstone message.
- `_send(topic, key, value)`: Sends one message to a topic.
- (optional) `_start()`: Opens connections or initializes other broker resources.
- (optional) `_stop()`: Closes connections or releases other broker resources.
- (optional) `_flush()`: Waits for pending messages if `_send()` returns before delivery is
  complete. The base class calls it after processing each received batch and before requesting the
  next batch, allowing consumed messages to be acknowledged only after the resulting messages have
  been delivered.

```python
from typing import AsyncIterable, List, Optional, Tuple

from nerdd_link import Channel


class ExampleChannel(Channel):
    def __init__(self, broker_url: str) -> None:
        super().__init__()
        self._broker_url = broker_url

    async def _start(self) -> None:
        # Connect to a broker.
        ...

    async def _stop(self) -> None:
        # Close the broker connection.
        ...

    async def _iter_messages(
        self, topic: str, consumer_group: str, batch_size: int
    ) -> AsyncIterable[List[Tuple[Optional[tuple], Optional[dict]]]]:
        while self.is_running:
            messages = ...

            # Hand messages over to processing.
            yield messages

            # Indicate successful completion, i.e. via committing or similar.

    async def _send(
        self, topic: str, key: Optional[tuple], value: Optional[dict]
    ) -> None:
        # Send the key and value to the broker.
        ...

    async def _flush(self) -> None:
        # Wait until all pending messages have been delivered.
        ...
```

Channel subclasses are registered when they are imported. The name is derived from the class name
by removing the `Channel` suffix and converting the remainder to snake case, so `ExampleChannel`
is selected with `--channel example`. Ensure that the module containing the new class is imported
when nerdd-link starts.

## Storage

The services use shared storage for molecular inputs, prediction checkpoints, and serialized
results. nerdd-link supports the local filesystem and S3-compatible object storage.

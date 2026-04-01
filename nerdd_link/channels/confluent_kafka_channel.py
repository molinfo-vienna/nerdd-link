import asyncio
import json
import logging
import time
from typing import Any, AsyncIterable, List, Optional, Tuple, Union, cast

from nerdd_link.utils import CommandQueueThread, command

from .channel import Channel

try:
    from confluent_kafka import Consumer, KafkaError, KafkaException, Producer, TopicPartition

    _IMPORT_ERROR: Optional[ImportError] = None
except ImportError as e:
    # This channel requires confluent-kafka to be installed. We store the ImportError in a variable
    # to avoid import errors when the library is missing, as long as this channel is not used.
    _IMPORT_ERROR = e


__all__ = ["ConfluentKafkaChannel"]

logger = logging.getLogger(__name__)


class _ProducerWorker(CommandQueueThread):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(name="confluent-kafka-producer", idle_timeout=5.0)
        self._config = config
        self._producer: Producer
        self._delivery_errors: list[BaseException] = []
        self._produce_errors: list[BaseException] = []

    def _initialize(self) -> None:
        self._producer = Producer(self._config)

    def _on_idle(self) -> None:
        self._producer.poll(0)

    def _shutdown(self) -> None:
        self._flush()

    @command(fire_and_forget=True)
    def produce(self, topic: str, key: Optional[bytes], value: Optional[bytes]) -> None:
        try:
            # try sending multiple times
            num_trials = 5
            for trial in range(num_trials):
                # if there are many produce operations in the worker queue, we might not
                # enter the "idle" command often enough -> poll once here
                self._producer.poll(0)

                # try sending
                try:
                    self._producer.produce(
                        topic,
                        key=key,
                        value=value,
                        callback=self._delivery_callback,
                    )
                    break
                except BaseException as error:
                    # give up when num_trials reached
                    if trial == num_trials - 1:
                        raise

                    # otherwise try one more time
                    logger.warning(
                        "Error while sending Kafka message. Retrying... (%s/%s): %s",
                        trial + 1,
                        num_trials,
                        error,
                    )
                    time.sleep(1)
        except BaseException as error:
            self._produce_errors.append(error)

    @command
    def flush(self) -> None:
        self._flush()

    def _flush(self) -> None:
        """Wait for pending deliveries and report producer failures."""
        try:
            remaining = self._producer.flush()
            if remaining != 0:
                raise RuntimeError(f"Kafka producer failed to deliver {remaining} message(s).")
            if self._delivery_errors:
                error = self._delivery_errors.pop(0)
                self._delivery_errors.clear()
                raise error
        finally:
            if self._produce_errors:
                error = self._produce_errors.pop(0)
                self._produce_errors.clear()
                raise error

    def _delivery_callback(self, error: Any, _: Any) -> None:
        if error is not None:
            self._delivery_errors.append(KafkaException(error))


class _ConsumerWorker(CommandQueueThread):
    """Poll one consumer while its current message batch is being processed."""

    def __init__(
        self,
        config: dict[str, Any],
        topic: str,
        batch_size: int,
    ) -> None:
        """Initialize a consumer worker.

        Parameters
        ----------
        config : dict[str, Any]
            Configuration passed to the confluent-kafka consumer.
        topic : str
            Topic to subscribe to.
        batch_size : int
            Maximum number of messages to deliver in one batch.
        """
        super().__init__(name=f"confluent-kafka-consumer-{topic}", idle_timeout=0.1)
        self._config = config
        self._topic = topic
        self._batch_size = batch_size

        self._consumer: Consumer
        self._pending: Optional[List[Any]] = None
        self._pending_offsets: dict[tuple[str, int], int] = {}
        self._failure: Optional[Exception] = None

    def _initialize(self) -> None:
        """Create and subscribe the consumer on its owning thread."""
        self._consumer = Consumer(self._config)
        self._consumer.subscribe(
            [self._topic],
            on_assign=self._on_assign,
            on_revoke=self._on_revoke,
        )

    def _on_assign(self, consumer: Consumer, partitions: List[Any]) -> None:
        """Pause partitions newly assigned while a batch is still running."""
        consumer.incremental_assign(partitions)

        # we need to pause newly assigned partitions if we are currently processing messages
        if self._pending is not None and len(partitions) > 0:
            consumer.pause(partitions)

    def _on_revoke(self, _: Consumer, partitions: List[Any]) -> None:
        """Invalidate the current batch's commit offsets for revoked partitions."""
        for partition in partitions:
            self._pending_offsets.pop((partition.topic, partition.partition), None)

    def _on_idle(self) -> None:
        """Service Kafka events even while the application processes a batch."""
        self._poll()

    def _poll(self, timeout: float = 0) -> None:
        """Poll once and retain at most one batch for the next fetch command."""
        if self._failure is not None:
            return

        try:
            messages = self._consumer.consume(
                num_messages=self._batch_size if self._pending is None else 1,
                timeout=timeout,
            )

            if len(messages) == 0:
                return

            # We might recover from these error codes later when committing.
            recoverable_codes = {
                KafkaError._PARTITION_EOF,
                KafkaError._TRANSPORT,
                KafkaError._WAIT_COORD,
                KafkaError._RESOLVE,
            }
            valid_messages = []
            for message in messages:
                error = message.error()
                if error is None:
                    valid_messages.append(message)
                elif not error.fatal() and error.code() in recoverable_codes:
                    logger.warning("Kafka consumer event: %s", error)
                else:
                    raise RuntimeError(f"Error while consuming Kafka message: {error}")

            if len(valid_messages) == 0:
                return

            if self._pending is not None:
                raise RuntimeError("Kafka returned a message while its partitions were paused")

            self._pending = valid_messages

            # For each (topic, partition) pair we store the maximum offset. When a partition is
            # revoked, we will remove them from this dictionary. When committing, we will commit
            # only (the offsets of) the remaining partitions
            self._pending_offsets = {}
            for message in valid_messages:
                partition_key = (message.topic(), message.partition())
                offset = message.offset() + 1
                if (
                    partition_key not in self._pending_offsets
                    or offset > self._pending_offsets[partition_key]
                ):
                    self._pending_offsets[partition_key] = offset

            # THE FOLLOWING CODE IS THE REASON WHY WE IMPLEMENTED _ConsumerWorker IN THE FIRST
            # PLACE: We pause fetching messages so each upcoming call to consume() will not retrieve
            # more messages, but it will keep communicating with kafka! That means we keep calling
            # consume() in the _on_idle slots of this command thread and have a much smaller value
            # for max.poll.interval.ms. In parallel, we use fetch() to get the current batch of
            # messages. When calling complete(), the messages are committed and consuming messages
            # is resumed.
            assignment = self._consumer.assignment()
            if len(assignment) > 0:
                self._consumer.pause(assignment)
        except Exception as error:
            self._failure = error

    @command
    def fetch(self) -> List[Any]:
        """Return the staged batch, polling briefly when no batch is ready.

        Returns
        -------
        List[Any]
            Kafka messages, or an empty list when no message is available yet.
        """
        # look for messages in the topic
        if self._pending is None:
            self._poll(timeout=0.5)

        # check for errors (remember: _poll doesn't raise errors but stores them in self._failure)
        if self._failure is not None:
            raise self._failure

        # if we are already processing messages (self._pending is not None) or the previous
        # self._poll did not yield messages, we return an empty list
        if self._pending is None:
            return []

        return self._pending

    def _shutdown(self) -> None:
        """Close the consumer on its owning thread."""
        self._consumer.close()

    @command
    def complete(self) -> bool:
        """Commit completed work on partitions owned continuously during the batch.

        Returns
        -------
        bool
            Whether the consumer must be recreated after repeated rebalance errors.
        """
        if self._failure is not None:
            raise self._failure

        if self._pending is None:
            raise RuntimeError("No Kafka message batch is awaiting completion")

        rebalance_codes = {
            KafkaError.ILLEGAL_GENERATION,
            KafkaError.UNKNOWN_MEMBER_ID,
            KafkaError.REBALANCE_IN_PROGRESS,
        }
        num_trials = 5
        for trial in range(num_trials):
            # Rebuild after polling: revoke callbacks may invalidate more batch offsets.
            offsets = [
                TopicPartition(topic, partition, offset)
                for (topic, partition), offset in self._pending_offsets.items()
            ]
            if len(offsets) == 0:
                break

            commit_error: Union[KafkaError, None] = None
            try:
                partitions = self._consumer.commit(offsets=offsets, asynchronous=False)

                # search for more errors in partitions
                if partitions is not None:
                    for partition in partitions:
                        if partition.error is None:
                            continue
                        commit_error = partition.error

                        # prioritize non-retriable errors
                        if not partition.error.retriable():
                            break
            except KafkaException as error:
                commit_error = cast(KafkaError, error.args[0])

            # check for errors
            if commit_error is None:
                break
            elif commit_error.code() in rebalance_codes:
                if trial + 1 >= num_trials:
                    logger.warning(
                        "Kafka commit repeatedly failed during rebalance; recreating consumer: %s",
                        commit_error,
                    )
                    return True
            elif not commit_error.retriable() or trial + 1 >= num_trials:
                raise RuntimeError(f"Error while committing Kafka message: {commit_error}")

            # error is retriable -> try one more time
            logger.warning(
                "Error while committing Kafka message. Retrying... (%s/%s): %s",
                trial + 1,
                num_trials,
                commit_error,
            )
            # Service rebalance callbacks while this command occupies the worker thread.
            self._poll(timeout=1.0)
            if self._failure is not None:
                raise self._failure

        self._pending = None
        self._pending_offsets.clear()

        # resume consuming messages
        assignment = self._consumer.assignment()
        if len(assignment) > 0:
            self._consumer.resume(assignment)

        # we don't need to handle a rebalance
        return False


class ConfluentKafkaChannel(Channel):
    def __init__(
        self,
        broker_url: str,
        broker_username: Optional[str] = None,
        broker_password: Optional[str] = None,
    ) -> None:
        super().__init__()
        if _IMPORT_ERROR is not None:
            raise _IMPORT_ERROR

        username_provided = broker_username is not None and broker_username.strip() != ""
        password_provided = broker_password is not None and broker_password.strip() != ""
        if username_provided != password_provided:
            raise ValueError(
                "Kafka broker authentication requires both broker_username and broker_password."
            )

        self._broker_url = broker_url
        self._broker_username = broker_username if username_provided else None
        self._broker_password = broker_password if password_provided else None
        self._producer_worker: Optional[_ProducerWorker] = None
        self._consumer_workers: set[_ConsumerWorker] = set()

    async def _start(self) -> None:
        auth_config = {}
        if self._broker_username is not None and self._broker_password is not None:
            auth_config = {
                "security.protocol": "SASL_PLAINTEXT",
                "sasl.mechanism": "PLAIN",
                "sasl.username": self._broker_username,
                "sasl.password": self._broker_password,
            }

        worker = _ProducerWorker(
            {
                "bootstrap.servers": self._broker_url,
                # ensure no messages are lost
                "acks": "all",
                # match aiokafka's default partitioner to allow seamless switching between the two
                "partitioner": "murmur2_random",
                # time until sending is considered failed
                "request.timeout.ms": 300_000,
                # optional authentication config
                **auth_config,
            }
        )
        self._producer_worker = worker
        worker.start()
        await asyncio.wrap_future(worker.initialized)
        logger.info("Kafka producer configured for broker %s.", self._broker_url)

    async def _stop(self) -> None:
        for consumer_worker in tuple(self._consumer_workers):
            try:
                await asyncio.wrap_future(consumer_worker.stop())
            except Exception:
                logger.error("Error while stopping consumer", exc_info=True)
            finally:
                await asyncio.to_thread(consumer_worker.join)
        self._consumer_workers.clear()

        worker = self._producer_worker
        if worker is None:
            return

        self._producer_worker = None
        try:
            await asyncio.wrap_future(worker.stop())
        finally:
            await asyncio.to_thread(worker.join)

    async def _iter_messages(
        self, topic: str, consumer_group: str, batch_size: int = 1
    ) -> AsyncIterable[List[Tuple[Optional[tuple], Optional[dict]]]]:
        auth_config = {}
        if self._broker_username is not None and self._broker_password is not None:
            auth_config = {
                "security.protocol": "SASL_PLAINTEXT",
                "sasl.mechanism": "PLAIN",
                "sasl.username": self._broker_username,
                "sasl.password": self._broker_password,
            }

        while True:
            if not self.is_running:
                logger.info("Shutdown event set for topic %s, stopping consumer...", topic)
                break

            worker = _ConsumerWorker(
                config={
                    "bootstrap.servers": self._broker_url,
                    "group.id": consumer_group,
                    "auto.offset.reset": "earliest",
                    "enable.auto.commit": False,
                    "enable.auto.offset.store": False,
                    # use cooperative sticky assignor to avoid being kicked out of the group during
                    # rebalances (-> decreases probability to interrupt long-running tasks)
                    "partition.assignment.strategy": "cooperative-sticky",
                    # max.poll.interval.ms: Time between polls before the consumer is considered
                    # dead. Since polling runs in parallel to long computations, we can keep this
                    # time interval short.
                    "max.poll.interval.ms": 5 * 60 * 1000,
                    # session.timeout.ms: The timeout used to detect failures when using Kafka's
                    # group management. We set this to 1 minute.
                    "session.timeout.ms": 60_000,
                    # heartbeat.interval.ms: The expected time between heartbeats to the consumer
                    # coordinator. The recommended value is 1/3 of session.timeout.ms.
                    "heartbeat.interval.ms": 20_000,
                    # optional authentication config
                    **auth_config,
                },
                topic=topic,
                batch_size=batch_size,
            )

            rebalance_needed = False
            self._consumer_workers.add(worker)
            worker.start()
            try:
                await asyncio.wrap_future(worker.initialized)
                logger.info(
                    "Connected to Kafka broker %s and started a consumer on topic %s.",
                    self._broker_url,
                    topic,
                )

                while True:
                    if not self.is_running:
                        logger.info("Shutdown event set for topic %s, stopping consumer...", topic)
                        break

                    # Fetch a batch from the worker while it continues polling Kafka.
                    messages = await asyncio.wrap_future(worker.fetch())
                    if len(messages) == 0:
                        continue

                    key_value_pairs = []
                    for message in messages:
                        message_key = message.key()
                        if message_key is None:
                            key = None
                        else:
                            try:
                                decoded_key: list[Any] = json.loads(message_key)
                            except json.JSONDecodeError:
                                # if we can't decode the key as JSON, we assume it is a string
                                decoded_key = [message_key.decode("utf-8")]
                            key = tuple(decoded_key)

                        # parse value
                        message_value = message.value()
                        value = None if message_value is None else json.loads(message_value)
                        key_value_pairs.append((key, value))

                    yield key_value_pairs

                    rebalance_needed = await asyncio.wrap_future(worker.complete())
                    if rebalance_needed:
                        break
            finally:
                logger.warning(
                    "Kafka consumer stopped on topic %s with group %s", topic, consumer_group
                )
                try:
                    await asyncio.wrap_future(worker.stop())
                except Exception:
                    logger.error("Error while stopping consumer", exc_info=True)
                finally:
                    await asyncio.to_thread(worker.join)
                    self._consumer_workers.discard(worker)

            if not rebalance_needed:
                break

    async def _send(self, topic: str, key: Optional[tuple], value: Optional[dict]) -> None:
        message_key = None if key is None else json.dumps(key).encode("utf-8")
        message_value = None if value is None else json.dumps(value).encode("utf-8")

        worker = self._producer_worker
        if worker is None:
            raise RuntimeError("Kafka producer not established.")

        # We don't wait until producing is finished. If an error occurs, we will catch it when
        # calling flush() later.
        worker.produce(topic, message_key, message_value)

    async def _flush(self) -> None:
        worker = self._producer_worker
        if worker is None:
            return

        await asyncio.wrap_future(worker.flush())

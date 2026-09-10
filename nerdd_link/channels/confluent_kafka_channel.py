import asyncio
import json
import logging
import time
from typing import Any, AsyncIterable, List, Optional, Tuple, Union, cast

from nerdd_link.utils import CommandQueueThread, command

from .channel import Channel

try:
    from confluent_kafka import Consumer, KafkaError, KafkaException, Producer

    _IMPORT_ERROR: Optional[ImportError] = None
except ImportError as e:
    # This channel requires confluent-kafka to be installed.
    # We define placeholders to avoid import errors when the library is missing,
    # as long as this channel is not used.
    _IMPORT_ERROR = e

    # We use classes as placeholders to avoid typing warnings like
    # "Variable not allowed in type expression"
    class Consumer:  # type: ignore
        pass

    class Producer:  # type: ignore
        pass

    class KafkaException(Exception):  # type: ignore
        pass

    class KafkaError:  # type: ignore
        ILLEGAL_GENERATION = 22
        UNKNOWN_MEMBER_ID = 25
        REBALANCE_IN_PROGRESS = 27


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
        pass

    @command(fire_and_forget=True)
    def produce(self, topic: str, key: Optional[bytes], value: Optional[bytes]) -> None:
        last_error: BaseException = RuntimeError(
            "Failed sending Kafka message after multiple trials."
        )
        try:
            num_trials = 5
            for trial in range(num_trials):
                try:
                    self._producer.produce(
                        topic,
                        key=key,
                        value=value,
                        callback=self._delivery_callback,
                    )
                except BaseException as error:
                    last_error = error
                    self._producer.poll(0)
                else:
                    break

                if trial < num_trials - 1:
                    logger.warning(
                        "Error while sending Kafka message. Retrying... (%s/%s): %s",
                        trial + 1,
                        num_trials,
                        last_error,
                    )
                    time.sleep(1)
            else:
                raise last_error
        except BaseException as error:
            self._produce_errors.append(error)
            raise

    @command
    def flush(self) -> None:
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

        rebalance_codes = {
            KafkaError.ILLEGAL_GENERATION,
            KafkaError.UNKNOWN_MEMBER_ID,
            KafkaError.REBALANCE_IN_PROGRESS,
        }

        while True:
            if not self.is_running:
                logger.info("Shutdown event set for topic %s, stopping consumer...", topic)
                break

            consumer = Consumer(
                {
                    "bootstrap.servers": self._broker_url,
                    "group.id": consumer_group,
                    "auto.offset.reset": "earliest",
                    "enable.auto.commit": False,
                    # use cooperative sticky assignor to avoid being kicked out of the group during
                    # rebalances (-> decreases probability to interrupt long-running tasks)
                    "partition.assignment.strategy": "cooperative-sticky",
                    # max.poll.interval.ms: Time between polls before the consumer is considered
                    # dead. Prediction tasks can take a long time, so we set this to 6 hours.
                    "max.poll.interval.ms": 6 * 60 * 60 * 1000,
                    # session.timeout.ms: The timeout used to detect failures when using Kafka's
                    # group management. We set this to 1 minute.
                    "session.timeout.ms": 60_000,
                    # heartbeat.interval.ms: The expected time between heartbeats to the consumer
                    # coordinator. The recommended value is 1/3 of session.timeout.ms.
                    "heartbeat.interval.ms": 20_000,
                    # optional authentication config
                    **auth_config,
                }
            )

            rebalance_needed = False
            try:
                await asyncio.to_thread(consumer.subscribe, [topic])
                logger.info(
                    "Connected to Kafka broker %s and started a consumer on topic %s.",
                    self._broker_url,
                    topic,
                )

                while True:
                    if not self.is_running:
                        logger.info("Shutdown event set for topic %s, stopping consumer...", topic)
                        break

                    # We run consumer.consume in a separate thread, because it would occupy the
                    # current event loop for (up to) the timeout duration. However, this doesn't
                    # spawn a new thread for each call (which would be expensive), but instead uses
                    # a thread pool.
                    messages = await asyncio.to_thread(
                        consumer.consume,
                        num_messages=batch_size,
                        timeout=0.5,
                    )

                    if len(messages) == 0:
                        continue

                    key_value_pairs = []
                    for message in messages:
                        error = message.error()
                        if error is not None:
                            raise RuntimeError(f"Error while consuming Kafka message: {error}")

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

                    # Commit message offsets. During this process, we often encounter errors that
                    # might be retriable. Therefore, we retry committing multiple times before
                    # giving up.
                    num_trials = 5
                    for trial in range(num_trials):
                        # In confluent-kafka, errors can be raised during consumer.commit() or
                        # returned in the list of partitions. We check both cases and store the
                        # error here.
                        commit_error: Union[KafkaError, None] = None

                        # try consumer.commit() and check errors
                        try:
                            partitions = await asyncio.to_thread(
                                consumer.commit, asynchronous=False
                            )
                        except KafkaException as error:
                            commit_error = cast(KafkaError, error.args[0])
                        # Check errors in the list of partitions. We store the most critical
                        # error (non-retriable > retriable) in the variable commit_error.
                        if commit_error is None and partitions is not None:
                            for partition in partitions:
                                if partition.error is None:
                                    continue
                                commit_error = partition.error

                                # If this error is retriable, there might still be a
                                # non-retriable error later, so we continue checking. Otherwise,
                                # we break early.
                                if not partition.error.retriable():
                                    break

                        # neither consumer.commit() nor the partitions contained an error
                        # -> we can break the retry loop
                        if commit_error is None:
                            break

                        if (
                            commit_error.code() in rebalance_codes
                            or commit_error in rebalance_codes
                        ):
                            logger.warning(
                                "Kafka commit failed due to consumer group rebalance (%s). "
                                "Re-subscribing consumer to obtain a fresh partition assignment...",
                                commit_error,
                            )
                            rebalance_needed = True
                            break

                        if not commit_error.retriable() or trial + 1 >= num_trials:
                            raise RuntimeError(
                                f"Error while committing Kafka message: {commit_error}"
                            )

                        logger.warning(
                            "Error while committing Kafka message. Retrying... (%s/%s): %s",
                            trial + 1,
                            num_trials,
                            commit_error,
                        )
                        await asyncio.sleep(1)

                    if rebalance_needed:
                        break
            finally:
                logger.warning(
                    "Kafka consumer stopped on topic %s with group %s", topic, consumer_group
                )
                try:
                    await asyncio.to_thread(consumer.close)
                except Exception:
                    logger.error("Error while stopping consumer", exc_info=True)

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

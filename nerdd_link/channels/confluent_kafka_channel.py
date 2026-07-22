import asyncio
import json
import logging
import time
from typing import Any, AsyncIterable, List, Optional, Tuple

from .channel import Channel

try:
    from confluent_kafka import Consumer, KafkaException, Producer

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


__all__ = ["ConfluentKafkaChannel"]

logger = logging.getLogger(__name__)


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
        self._producer: Optional[Producer] = None

    async def _start(self) -> None:
        auth_config = {}
        if self._broker_username is not None and self._broker_password is not None:
            auth_config = {
                "security.protocol": "SASL_PLAINTEXT",
                "sasl.mechanism": "PLAIN",
                "sasl.username": self._broker_username,
                "sasl.password": self._broker_password,
            }

        self._producer = Producer(
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
        logger.info(f"Kafka producer configured for broker {self._broker_url}.")

    async def _stop(self) -> None:
        if self._producer is None:
            return

        self._producer = None

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

        try:
            await asyncio.to_thread(
                consumer.subscribe,
                [topic],
            )

            logger.info(
                f"Connected to Kafka broker {self._broker_url} and started a consumer on topic "
                f"{topic}."
            )

            while True:
                if not self.is_running:
                    logger.info(f"Shutdown event set for topic {topic}, stopping consumer...")
                    break

                # We run consumer.consume in a separate thread, because it would occupy the current
                # event loop for (up to) the timeout duration. However, this doesn't spawn a new
                # thread for each call (which would be expensive), but instead uses a thread pool.
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

                    # parse key
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
                    if message_value is None:
                        value = None
                    else:
                        value = json.loads(message_value)

                    key_value_pairs.append((key, value))

                yield key_value_pairs

                # Commit message offsets. During this process, we often encounter errors that might
                # be retriable. Therefore, we retry committing multiple times before giving up.
                n_trials = 5
                for trial in range(n_trials):
                    # In confluent-kafka, errors can be raised during consumer.commit() or
                    # returned in the list of partitions. We check both cases and store the
                    # error here.
                    commit_error = None

                    # try consumer.commit() and check errors
                    try:
                        partitions = await asyncio.to_thread(
                            consumer.commit,
                            asynchronous=False,
                        )
                    except KafkaException as error:
                        commit_error = error.args[0]
                    else:
                        # Check errors in the list of partitions. We store the most critical error
                        # (non-retriable > retriable) in the variable commit_error.
                        if partitions is not None:
                            for partition in partitions:
                                if partition.error is None:
                                    continue

                                commit_error = partition.error

                                # If this error is retriable, there might still be a non-retriable
                                # error later, so we continue checking. Otherwise, we break early.
                                if not partition.error.retriable():
                                    break

                    if commit_error is None:
                        # neither consumer.commit() nor the partitions contained an error
                        # -> we can break the retry loop
                        break
                    elif not commit_error.retriable() or trial + 1 >= n_trials:
                        # there was a non-retriable error or we have no trials left
                        raise RuntimeError(f"Error while committing Kafka message: {commit_error}")
                    else:
                        # error is retriable and we have trials left
                        logger.warning(
                            "Error while committing Kafka message. Retrying... (%s/%s): %s",
                            trial + 1,
                            n_trials,
                            commit_error,
                        )
                        await asyncio.sleep(1)
        finally:
            logger.warning(
                "Kafka consumer stopped on topic %s with group %s",
                topic,
                consumer_group,
            )
            try:
                await asyncio.to_thread(consumer.close)
            except Exception:
                logger.error("Error while stopping consumer", exc_info=True)

    async def _send(self, topic: str, key: Optional[tuple], value: Optional[dict]) -> None:
        # store self._producer in a local variable to avoid issues with parallel shutdown
        # (stopping the channel sets self._producer to None)
        producer = self._producer
        if producer is None:
            raise RuntimeError("Kafka producer not established.")

        # compute key
        if key is None:
            message_key = None
        else:
            message_key = json.dumps(key).encode("utf-8")

        # compute value
        if value is None:
            message_value = None
        else:
            message_value = json.dumps(value).encode("utf-8")

        def produce_and_flush() -> None:
            n_trials = 5

            # define an exception that will be raised if all trials fail
            last_error: BaseException = RuntimeError(
                "Failed sending message after multiple trials."
            )

            # try sending multiple times before giving up
            for trial in range(n_trials):
                delivery_error = None

                def delivery_callback(error: Any, message: Any) -> None:
                    nonlocal delivery_error
                    if error is not None:
                        delivery_error = error

                try:
                    producer.produce(
                        topic,
                        key=message_key,
                        value=message_value,
                        callback=delivery_callback,
                    )
                    producer.flush()

                    if delivery_error is None:
                        return

                    last_error = KafkaException(delivery_error)
                except Exception as error:
                    last_error = error

                if trial + 1 < n_trials:
                    logger.warning(
                        f"Error while sending Kafka message. Retrying... "
                        f"({trial + 1}/{n_trials}): {last_error}"
                    )
                    time.sleep(1)

            raise last_error

        await asyncio.to_thread(produce_and_flush)

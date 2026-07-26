import asyncio
import json
import logging
from typing import Any, AsyncIterable, Dict, List, Optional, Tuple, Union
from urllib.parse import unquote, urlparse

try:
    from rstream import (
        AMQPMessage,
        Consumer,
        ConsumerOffsetSpecification,
        MessageContext,
        OffsetNotFound,
        OffsetType,
        Producer,
        amqp_decoder,
    )

    _IMPORT_ERROR: Optional[ImportError] = None
except ImportError as e:
    # This channel requires rstream to be installed. We define placeholders to
    # avoid import errors when the library is missing, as long as this channel
    # is not used.
    _IMPORT_ERROR = e

    # We use classes as placeholders to avoid typing warnings like
    # "Variable not allowed in type expression".
    class AMQPMessage:  # type: ignore
        pass

    class Consumer:  # type: ignore
        pass

    class ConsumerOffsetSpecification:  # type: ignore
        pass

    class MessageContext:  # type: ignore
        pass

    class OffsetNotFound(Exception):  # type: ignore
        pass

    class OffsetType:  # type: ignore
        pass

    class Producer:  # type: ignore
        pass

    def amqp_decoder(*args, **kwargs):  # type: ignore
        pass


from .channel import Channel

__all__ = ["RabbitmqStreamsChannel"]

logger = logging.getLogger(__name__)

_KEY_HEADER = b"x-nerdd-key"
_DEFAULT_RABBITMQ_PORT = 5552


class RabbitmqStreamsChannel(Channel):
    def __init__(
        self,
        broker_url: str,
        broker_username: Optional[str] = None,
        broker_password: Optional[str] = None,
    ) -> None:
        if _IMPORT_ERROR is not None:
            raise ImportError(
                "RabbitmqStreamsChannel requires 'rstream' to be installed. "
                "Install it with 'pip install rstream'."
            ) from _IMPORT_ERROR

        super().__init__()

        parsed_url = urlparse(broker_url)

        # validate scheme
        if parsed_url.scheme != "rabbitmq":
            raise ValueError(
                f"Invalid URL scheme '{parsed_url.scheme}' for RabbitmqStreamsChannel. "
                f"Expected 'rabbitmq'."
            )

        # use default host and port if not specified
        self._host = parsed_url.hostname or "localhost"
        self._port = parsed_url.port or _DEFAULT_RABBITMQ_PORT

        # username and password: percent-decode from URL using unquote (e.g. p%40ssword -> p@ssword)
        self._username = (
            broker_username
            if broker_username is not None
            else (unquote(parsed_url.username) if parsed_url.username else "guest")
        )
        self._password = (
            broker_password
            if broker_password is not None
            else (unquote(parsed_url.password) if parsed_url.password else "guest")
        )

        self._producer: Optional[Producer] = None

    async def _start(self) -> None:
        self._producer = Producer(
            self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            connection_name="nerdd-link-producer",
        )
        await self._producer.start()
        logger.info(
            "RabbitMQ stream producer started on %s:%s.",
            self._host,
            self._port,
        )

    async def _stop(self) -> None:
        if self._producer is not None:
            await self._producer.close()
            self._producer = None

    async def _iter_messages(
        self, topic: str, consumer_group: str, batch_size: int = 1
    ) -> AsyncIterable[List[Tuple[Optional[tuple], Optional[dict]]]]:
        if self._producer is None:
            raise RuntimeError("RabbitMQ producer not established.")

        consumer = Consumer(
            self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            connection_name=f"nerdd-link-{consumer_group}",
        )
        subscriber_name = consumer_group
        message_queue: asyncio.Queue[Tuple[int, AMQPMessage]] = asyncio.Queue(
            maxsize=max(batch_size * 10, 100)
        )

        async def on_message(message: AMQPMessage, context: MessageContext) -> None:
            offset = context.offset
            await message_queue.put((offset, message))

        try:
            await self._producer.create_stream(topic, exists_ok=True)

            try:
                stored_offset = await consumer.query_offset(topic, subscriber_name)
            except OffsetNotFound:
                offset_specification = ConsumerOffsetSpecification(OffsetType.FIRST, None)
            else:
                offset_specification = ConsumerOffsetSpecification(
                    OffsetType.OFFSET, stored_offset + 1
                )

            await consumer.subscribe(
                stream=topic,
                subscriber_name=subscriber_name,
                callback=on_message,
                decoder=amqp_decoder,
                offset_specification=offset_specification,
                initial_credit=max(batch_size, 1),
            )

            logger.info(
                "RabbitMQ stream consumer started on stream %s with group %s.",
                topic,
                consumer_group,
            )

            while True:
                if not self.is_running:
                    logger.info(
                        "Shutdown event set for RabbitMQ topic %s, stopping consumer...", topic
                    )
                    break

                try:
                    first_message = await asyncio.wait_for(message_queue.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue

                messages = [first_message]
                while len(messages) < batch_size:
                    try:
                        messages.append(message_queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

                key_value_pairs = []
                for _, message in messages:
                    # decode key
                    application_properties = message.application_properties or {}
                    if _KEY_HEADER in application_properties:
                        raw_key = application_properties[_KEY_HEADER]
                        try:
                            key = tuple(json.loads(raw_key))
                        except (json.JSONDecodeError, TypeError):
                            # key is not a valid JSON object, i.e. a string without quotes
                            # -> use the key as is (but decode to str if it's bytes)
                            if isinstance(raw_key, bytes):
                                raw_key = raw_key.decode("utf-8")
                            key = (str(raw_key),)
                    else:
                        key = None

                    # decode value
                    if message.body is None:
                        value = None
                    else:
                        value = json.loads(message.body)

                    key_value_pairs.append((key, value))

                yield key_value_pairs

                await consumer.store_offset(topic, subscriber_name, messages[-1][0])
        finally:
            await consumer.close()

    async def _send(self, topic: str, key: Optional[tuple], value: Optional[dict]) -> None:
        if self._producer is None:
            raise RuntimeError("RabbitMQ producer not established.")

        await self._producer.create_stream(topic, exists_ok=True)

        # encode key
        application_properties: Dict[Union[str, bytes], Any] = {}
        if key is not None:
            application_properties[_KEY_HEADER] = json.dumps(key).encode("utf-8")

        # encode body
        if value is None:
            body = None
        else:
            body = json.dumps(value).encode("utf-8")

        message = AMQPMessage(body=body, application_properties=application_properties)
        await self._producer.send_wait(topic, message)

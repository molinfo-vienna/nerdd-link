import asyncio
import json
import logging
import ssl
from typing import AsyncIterable, List, Optional, Tuple
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

_KEY_HEADER = "x-nerdd-key"
_DEFAULT_RABBITMQ_PORT = 5552
_DEFAULT_RABBITMQ_TLS_PORT = 5551


class RabbitmqStreamsChannel(Channel):
    def __init__(
        self,
        broker_url: str,
        broker_username: Optional[str] = None,
        broker_password: Optional[str] = None,
    ) -> None:
        super().__init__()
        if _IMPORT_ERROR is not None:
            raise _IMPORT_ERROR

        self._broker_url = broker_url

        parsed = urlparse(broker_url)
        if parsed.scheme not in {"rabbitmq", "rabbitmqs"}:
            raise ValueError(f"Unsupported RabbitMQ broker URL scheme: {parsed.scheme}")

        host = parsed.hostname
        if host is None:
            raise ValueError(f"Invalid RabbitMQ broker URL: {broker_url}")
        self._host = host

        use_tls = parsed.scheme == "rabbitmqs"
        self._ssl_context = ssl.create_default_context() if use_tls else None

        default_port = _DEFAULT_RABBITMQ_TLS_PORT if use_tls else _DEFAULT_RABBITMQ_PORT
        self._port = parsed.port or default_port

        self._username = broker_username or unquote(parsed.username or "guest")
        self._password = broker_password or unquote(parsed.password or "guest")
        self._vhost = unquote(parsed.path[1:]) if parsed.path not in {"", "/"} else "/"

        self._producer: Optional[Producer] = None

    async def _start(self) -> None:
        self._producer = Producer(
            self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            vhost=self._vhost,
            ssl_context=self._ssl_context,
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
            vhost=self._vhost,
            ssl_context=self._ssl_context,
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
                    key_value_pairs.append(
                        (
                            self._decode_key(message),
                            self._decode_value(message),
                        )
                    )

                yield key_value_pairs

                await consumer.store_offset(topic, subscriber_name, messages[-1][0])
        finally:
            await consumer.close()

    async def _send(self, topic: str, key: Optional[tuple], value: Optional[dict]) -> None:
        if self._producer is None:
            raise RuntimeError("RabbitMQ producer not established.")

        await self._producer.create_stream(topic, exists_ok=True)

        if value is None:
            body = b""
        else:
            body = json.dumps(value).encode("utf-8")

        application_properties = {}
        if key is not None:
            application_properties[_KEY_HEADER] = json.dumps(key)

        message = AMQPMessage(body=body, application_properties=application_properties)
        await self._producer.send_wait(topic, message)

    @staticmethod
    def _decode_key(message: AMQPMessage) -> Optional[tuple]:
        application_properties = message.application_properties or {}
        if _KEY_HEADER not in application_properties:
            return None

        raw_key = application_properties[_KEY_HEADER]
        try:
            return tuple(json.loads(str(raw_key)))
        except (json.JSONDecodeError, TypeError):
            return (str(raw_key),)

    @staticmethod
    def _decode_value(message: AMQPMessage) -> Optional[dict]:
        if message.body in (None, b""):
            return None
        return json.loads(message.body)

import json
import logging
from typing import Optional, AsyncIterator
import asyncio

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from ..types import Message
from .channel import Channel

__all__ = ["KafkaChannel"]

logger = logging.getLogger(__name__)


class KafkaChannel(Channel):
    def __init__(self, broker_url):
        super().__init__()
        self._broker_url = broker_url
        self._consumers = {}

        self._producer = AIOKafkaProducer(
            bootstrap_servers=[self._broker_url],
        )
        asyncio.create_task(self._producer.start())
        logger.info(f"Connecting to Kafka broker {self._broker_url} and starting a producer.")

    async def _iter_messages(self, topic: str, consumer_group: Optional[str] = None) -> AsyncIterator[Message]:
        if consumer_group is not None:
            consumer_group = f"{consumer_group}-consumer-group"

        key = (topic, consumer_group)

        if key not in self._consumers:
            # create consumer
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=[self._broker_url],
                auto_offset_reset="earliest",
                group_id=consumer_group,
                enable_auto_commit=False,
            )
            await consumer.start()
            self._consumers[key] = consumer
            logger.info(
                f"Connecting to Kafka broker {self._broker_url} and starting a consumer on "
                f"topic {topic}."
            )

        consumer = self._consumers[key]

        try:
            async for message in consumer:
                message_obj = json.loads(message.value)
                yield Message(**message_obj)
                await consumer.commit()
        finally:
            await consumer.stop()

    async def _send(self, topic: str, message: Message) -> None:
        await self._producer.send_and_wait(
            topic,
            json.dumps(message.model_dump()).encode("utf-8"),
        )

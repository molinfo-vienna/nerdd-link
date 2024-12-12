import json
import logging
from typing import AsyncIterable, Dict, Tuple

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from ..types import Message
from .channel import Channel

__all__ = ["KafkaChannel"]

logger = logging.getLogger(__name__)


class KafkaChannel(Channel):
    def __init__(self, broker_url: str) -> None:
        super().__init__()
        self._broker_url = broker_url
        self._consumers: Dict[Tuple[str, str], AIOKafkaConsumer] = {}

    async def _start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=[self._broker_url],
            value_serializer=lambda v: json.dumps(v.model_dump()).encode("utf-8"),
        )
        logger.info(f"Connecting to Kafka broker {self._broker_url} and starting a producer...")
        await self._producer.start()

        for consumer in self._consumers.values():
            await consumer.start()

    async def _stop(self) -> None:
        await self._producer.stop()
        for consumer in self._consumers.values():
            await consumer.stop()

    async def _iter_messages(self, topic: str, consumer_group: str) -> AsyncIterable[Message]:
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

        # try:
        #     while True:
        #         # we use polling (instead of iterating through the consumer messages)
        #         # to be able to cancel the consumer
        #         messages = await self.kafka_consumer.getmany(timeout_ms=1000)

        #         if messages:
        #             for _, message_list in messages.items():
        #                 for message in message_list:
        #                     result = json.loads(message.value)
        #                     logger.info(f"Received message on {message.topic}")

        #                     try:
        #                         for consumer in self.consumers:
        #                             await consumer.consume(result)

        #                         logger.info("Committing message")
        #                         await self.kafka_consumer.commit()
        #                     except Exception:
        #                         logger.info("Rolling back message")
        #                         logger.error(traceback.format_exc())
        # except asyncio.CancelledError:
        #     logger.info("Stopping ConsumeKafkaTopicLifespan")
        #     await self.kafka_consumer.stop()
        # except Exception as e:
        #     logger.error(e)
        #     logger.error(traceback.format_exc())

    async def _send(self, topic: str, message: Message) -> None:
        await self._producer.send_and_wait(
            topic,
            message,
        )

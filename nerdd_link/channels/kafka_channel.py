import json
import logging
from typing import Iterator, Optional

from kafka import KafkaConsumer, KafkaProducer

from ..types import Message
from .channel import Channel

__all__ = ["KafkaChannel"]

logger = logging.getLogger(__name__)


class KafkaChannel(Channel):
    def __init__(self, broker_url):
        super().__init__()
        self._broker_url = broker_url
        self._consumers = {}

        self._producer = KafkaProducer(
            bootstrap_servers=[self._broker_url],
            api_version=(3, 3, 1),
        )
        logger.info(f"Connecting to Kafka broker {self._broker_url} and starting a producer.")

    def _iter_messages(self, topic: str, consumer_group: Optional[str] = None) -> Iterator[Message]:
        if consumer_group is not None:
            consumer_group = f"{consumer_group}-consumer-group"

        key = (topic, consumer_group)

        if key not in self._consumers:
            # create consumer
            self._consumers[key] = KafkaConsumer(
                topic,
                bootstrap_servers=[self._broker_url],
                api_version=(3, 3, 1),
                auto_offset_reset="earliest",
                group_id=consumer_group,
                enable_auto_commit=False,
                max_poll_records=1,
            )
            logger.info(
                f"Connecting to Kafka broker {self._broker_url} and starting a consumer on "
                f"topic {topic}."
            )

        consumer = self._consumers[key]

        while True:
            # fetch one tuple
            messages = consumer.poll(timeout_ms=1000)

            if messages:
                logger.info(f"Received {len(messages)} messages")

                for _, message_list in messages.items():
                    for message in message_list:
                        message_obj = json.loads(message.value)
                        yield Message(**message_obj)

                # commit the message offsets we have processed
                consumer.commit()

    def _send(self, topic: str, message: Message) -> None:
        future = self._producer.send(
            topic,
            json.dumps(message.model_dump()).encode("utf-8"),
        )

        # wait for the message to be sent
        future.get()

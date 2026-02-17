from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Optional

class AMQPMessage:
    body: bytes
    application_properties: Optional[Mapping[str, Any]]

    def __init__(
        self,
        body: bytes,
        application_properties: Optional[Mapping[str, Any]] = ...,
    ) -> None: ...

class MessageContext:
    offset: int

class OffsetNotFound(Exception): ...

class OffsetType:
    FIRST: OffsetType
    OFFSET: OffsetType

class ConsumerOffsetSpecification:
    def __init__(self, offset_type: OffsetType, offset: Optional[int]) -> None: ...

class Consumer:
    def __init__(
        self,
        host: str,
        *,
        port: int,
        username: str,
        password: str,
        vhost: str,
        ssl_context: Any,
        connection_name: str,
    ) -> None: ...
    async def query_offset(self, stream: str, reference: str) -> int: ...
    async def subscribe(
        self,
        *,
        stream: str,
        subscriber_name: str,
        callback: Callable[[AMQPMessage, MessageContext], Awaitable[None]],
        decoder: Callable[[bytes], AMQPMessage],
        offset_specification: ConsumerOffsetSpecification,
        initial_credit: int,
    ) -> None: ...
    async def store_offset(self, stream: str, reference: str, offset: int) -> None: ...
    async def close(self) -> None: ...

class Producer:
    def __init__(
        self,
        host: str,
        *,
        port: int,
        username: str,
        password: str,
        vhost: str,
        ssl_context: Any,
        connection_name: str,
    ) -> None: ...
    async def start(self) -> None: ...
    async def create_stream(self, stream: str, *, exists_ok: bool) -> None: ...
    async def send_wait(self, stream: str, message: AMQPMessage) -> None: ...
    async def close(self) -> None: ...

def amqp_decoder(data: bytes) -> AMQPMessage: ...

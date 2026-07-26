from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any, Dict, Optional, Union

class AMQPMessage:
    body: Optional[bytes]
    application_properties: Optional[Dict[Union[str, bytes], Any]]
    publishing_id: Optional[int]

    def __init__(
        self,
        *,
        application_properties: Optional[Dict[Union[str, bytes], Any]] = ...,
        body: Optional[bytes] = ...,
        publishing_id: Optional[int] = ...,
    ) -> None: ...
    def __bytes__(self) -> bytes: ...
    def __str__(self) -> str: ...

class MessageContext:
    offset: int

class OffsetNotFound(Exception): ...

class OffsetType(int, Enum):
    FIRST = 1
    OFFSET = 4

class ConsumerOffsetSpecification:
    offset_type: OffsetType
    offset: Optional[int]

    def __init__(self, offset_type: OffsetType = ..., offset: Optional[int] = ...) -> None: ...

class Consumer:
    def __init__(
        self,
        host: str,
        port: int = ...,
        *,
        username: str,
        password: str,
        connection_name: str = ...,
    ) -> None: ...
    async def query_offset(self, stream: str, subscriber_name: str) -> int: ...
    async def subscribe(
        self,
        stream: str,
        callback: Callable[[AMQPMessage, MessageContext], Union[None, Awaitable[None]]],
        *,
        decoder: Optional[Callable[[bytes], Any]] = ...,
        offset_specification: Optional[ConsumerOffsetSpecification] = ...,
        initial_credit: int = ...,
        subscriber_name: Optional[str] = ...,
    ) -> int: ...
    async def store_offset(self, stream: str, subscriber_name: str, offset: int) -> None: ...
    async def close(self) -> None: ...

class Producer:
    def __init__(
        self,
        host: str,
        port: int = ...,
        *,
        username: str,
        password: str,
        connection_name: str = ...,
    ) -> None: ...
    async def start(self) -> None: ...
    async def create_stream(
        self,
        stream: str,
        arguments: Optional[Dict[str, Any]] = ...,
        exists_ok: bool = ...,
    ) -> None: ...
    async def send_wait(
        self,
        stream: str,
        message: Union[AMQPMessage, bytes],
        publisher_name: Optional[str] = ...,
        timeout: Optional[int] = ...,
    ) -> int: ...
    async def close(self) -> None: ...

def amqp_decoder(data: bytes) -> AMQPMessage: ...

import asyncio

import pytest

from nerdd_link import MemoryChannel, Message


@pytest.mark.asyncio
async def test_consumer_groups_in_memory_channel():
    async with MemoryChannel() as channel:
        # send one message
        await channel.send("topic", Message(content="message1"))

        #
        # check that the message is received by both consumer groups
        #
        i = 0
        async for _ in channel.iter_messages("topic", "group1"):
            i += 1
            break

        assert i == 1

        i = 0
        async for _ in channel.iter_messages("topic", "group2"):
            i += 1
            break

        assert i == 1

        #
        # check that the message is not received again
        #
        async def _receive():
            async for _ in channel.iter_messages("topic", "group2"):
                return

        # the call to _receive should timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(_receive(), timeout=0.1)
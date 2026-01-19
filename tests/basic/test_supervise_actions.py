import asyncio

import pytest

from nerdd_link.actions import supervise_actions
from nerdd_link.channels.memory_channel import MemoryChannel


class FakeAction:
    def __init__(self, channel, results):
        self.channel = channel
        self.results = list(results)
        self.run_calls = 0

    async def run(self):
        self.run_calls += 1
        return await self._run()

    async def _run(self):
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    def __repr__(self):
        return f"FakeAction(run_calls={self.run_calls})"


class WaitingAction(FakeAction):
    def __init__(self, channel, results):
        super().__init__(channel, results)
        self.finished = asyncio.Event()

    async def _run(self):
        try:
            await asyncio.Event().wait()
        finally:
            self.finished.set()


@pytest.mark.asyncio
async def test_supervise_actions_restarts_successful_action_when_channel_is_running():
    class StoppingOnSecondRunAction(FakeAction):
        async def _run(self):
            await super()._run()
            if self.run_calls == 2:
                await self.channel.stop()
            return None

    channel = MemoryChannel()
    await channel.start()
    action = StoppingOnSecondRunAction(channel, [None, None])

    await supervise_actions([action], max_retries=5)

    assert action.run_calls == 2


@pytest.mark.asyncio
async def test_supervise_actions_raises_runtime_error_when_clean_exit_exhausts_retries():
    channel = MemoryChannel()
    await channel.start()
    action = FakeAction(channel, [None, None])

    with pytest.raises(RuntimeError, match="Action finished unexpectedly"):
        await supervise_actions([action], max_retries=1)

    assert action.run_calls == 2


@pytest.mark.asyncio
async def test_supervise_actions_raises_after_max_retries_are_exhausted():
    channel = MemoryChannel()
    await channel.start()
    action = FakeAction(channel, [RuntimeError("failed"), RuntimeError("failed again")])

    with pytest.raises(RuntimeError, match="failed again"):
        await supervise_actions([action], max_retries=1)

    assert action.run_calls == 2


@pytest.mark.asyncio
async def test_supervise_actions_restarts_failed_action_indefinitely_when_retries_are_none():
    class StoppingOnThirdRunAction(FakeAction):
        async def _run(self):
            await super()._run()
            if self.run_calls == 3:
                await self.channel.stop()
            return None

    channel = MemoryChannel()
    await channel.start()
    action = StoppingOnThirdRunAction(
        channel,
        [
            RuntimeError("failed once"),
            RuntimeError("failed twice"),
            None,
        ],
    )

    await supervise_actions([action], max_retries=None)

    assert action.run_calls == 3


@pytest.mark.asyncio
async def test_supervise_actions_cancels_other_actions_when_retries_are_exhausted():
    channel = MemoryChannel()
    await channel.start()
    failing_action = FakeAction(channel, [RuntimeError("failed")])
    waiting_action = WaitingAction(channel, [])

    with pytest.raises(RuntimeError, match="failed"):
        await supervise_actions([failing_action, waiting_action], max_retries=0)

    assert waiting_action.run_calls == 1
    assert waiting_action.finished.is_set()


@pytest.mark.asyncio
async def test_supervise_actions_does_not_restart_failed_action_when_channel_is_stopped():
    channel = MemoryChannel()
    # We do not call channel.start(), so the channel starts in a stopped/stopping state.
    action = FakeAction(channel, [RuntimeError("failed during shutdown")])

    await supervise_actions([action], max_retries=None)

    assert action.run_calls == 1


@pytest.mark.asyncio
async def test_supervise_actions_empty_actions():
    await supervise_actions([], max_retries=5)

from collections.abc import Iterator
from queue import Full
from threading import Event, get_ident

import pytest

from nerdd_link.utils import CommandQueueThread, command


class ExampleCommandQueueThread(CommandQueueThread):
    def __init__(self) -> None:
        super().__init__(name="example-command-queue", idle_timeout=0.01)
        self.events: list[str] = []
        self.idle = Event()
        self.release = Event()

    def _initialize(self) -> None:
        self.events.append("initialized")

    def _on_idle(self) -> None:
        self.idle.set()

    def _shutdown(self) -> None:
        self.events.append("stopped")

    @command
    def add(self, left: int, right: int) -> tuple[int, int]:
        return left + right, get_ident()

    @command
    def fail(self) -> None:
        raise RuntimeError("command failed")

    @command
    def wait(self) -> None:
        self.release.wait()

    @command
    def wait_and_fail(self) -> None:
        self.release.wait()
        raise RuntimeError("command failed")

    @command(fire_and_forget=True)
    def record(self, event: str) -> None:
        self.events.append(event)

    @command(fire_and_forget=True)
    def fail_fire_and_forget(self) -> None:
        raise RuntimeError("fire-and-forget command failed")


class SlowCommandQueueThread(CommandQueueThread):
    def __init__(self) -> None:
        self.initialization_started = Event()
        self.release_initialization = Event()
        self.shutdown_started = Event()
        self.release_shutdown = Event()
        super().__init__()

    def _initialize(self) -> None:
        self.initialization_started.set()
        self.release_initialization.wait()

    def _shutdown(self) -> None:
        self.shutdown_started.set()
        self.release_shutdown.wait()


class FailingInitializationCommandQueueThread(CommandQueueThread):
    def _initialize(self) -> None:
        raise RuntimeError("initialization failed")


class FailingShutdownCommandQueueThread(CommandQueueThread):
    def _shutdown(self) -> None:
        raise RuntimeError("shutdown failed")


@pytest.fixture
def worker() -> Iterator[ExampleCommandQueueThread]:
    worker = ExampleCommandQueueThread()
    worker.start()
    worker.initialized.result(timeout=1)

    try:
        yield worker
    finally:
        # Also unblock the worker if the test failed before releasing a wait command.
        worker.release.set()
        worker.stop().result(timeout=1)
        worker.join(timeout=1)
        assert not worker.is_alive()


# Construction


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_queue_size": 0}, "max_queue_size must be greater than zero"),
        ({"idle_timeout": 0}, "idle_timeout must be greater than zero"),
    ],
)
def test_rejects_invalid_configuration(kwargs: dict[str, int], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        CommandQueueThread(**kwargs)


# Initialization


def test_initialization_and_shutdown_hooks() -> None:
    worker = ExampleCommandQueueThread()
    worker.start()

    try:
        worker.initialized.result(timeout=1)
        assert worker.events == ["initialized"]
    finally:
        worker.stop().result(timeout=1)
        worker.join(timeout=1)
        assert not worker.is_alive()

    assert worker.events == ["initialized", "stopped"]


def test_initialization_failure_rejects_and_fails_pending_commands() -> None:
    worker = FailingInitializationCommandQueueThread()
    pending = worker.submit(lambda: None)
    worker.start()

    try:
        with pytest.raises(RuntimeError, match="initialization failed"):
            worker.initialized.result(timeout=1)
        with pytest.raises(RuntimeError, match="initialization failed"):
            pending.result(timeout=1)

        worker.join(timeout=1)
        assert not worker.is_alive()

        with pytest.raises(RuntimeError, match="after shutdown has started"):
            worker.submit(lambda: None)

        stopped = worker.stop()
        assert stopped.result(timeout=1) is None
        assert worker.stop() is stopped
    finally:
        worker.join(timeout=1)
        assert not worker.is_alive()


def test_stop_during_initialization_does_not_resume_accepting_commands() -> None:
    worker = SlowCommandQueueThread()
    worker.start()
    try:
        assert worker.initialization_started.wait(timeout=1)

        stopped = worker.stop()
        worker.release_initialization.set()
        worker.initialized.result(timeout=1)
        assert worker.shutdown_started.wait(timeout=1)

        with pytest.raises(RuntimeError, match="after shutdown has started"):
            worker.submit(lambda: None)

        worker.release_shutdown.set()
        stopped.result(timeout=1)
    finally:
        worker.release_initialization.set()
        worker.release_shutdown.set()
        worker.stop().result(timeout=1)
        worker.join(timeout=1)
        assert not worker.is_alive()


# Shutdown


def test_stop_is_idempotent_and_rejects_new_commands() -> None:
    worker = ExampleCommandQueueThread()
    worker.start()
    worker.initialized.result(timeout=1)

    try:
        waiting = worker.wait()
        stopped = worker.stop()

        with pytest.raises(RuntimeError, match="after shutdown has started"):
            worker.add(2, 3)

        assert worker.stop() is stopped

        worker.release.set()
        waiting.result(timeout=1)
        stopped.result(timeout=1)
    finally:
        worker.release.set()
        worker.stop().result(timeout=1)
        worker.join(timeout=1)
        assert not worker.is_alive()


def test_shutdown_exception_is_returned_by_stop() -> None:
    worker = FailingShutdownCommandQueueThread()
    worker.start()
    worker.initialized.result(timeout=1)

    try:
        with pytest.raises(RuntimeError, match="shutdown failed"):
            worker.stop().result(timeout=1)
    finally:
        worker.join(timeout=1)
        assert not worker.is_alive()


# Submit tasks


def test_decorated_command_runs_on_thread_and_completes_future(
    worker: ExampleCommandQueueThread,
) -> None:
    result, thread_id = worker.add(2, 3).result(timeout=1)

    assert result == 5
    assert thread_id == worker.ident


def test_submitted_callable_runs_on_thread(worker: ExampleCommandQueueThread) -> None:
    result, thread_id = worker.submit(
        lambda left, right: (left + right, get_ident()), 2, right=3
    ).result(timeout=1)

    assert result == 5
    assert thread_id == worker.ident


def test_fire_and_forget_command_runs_without_returning_future(
    worker: ExampleCommandQueueThread,
) -> None:
    assert worker.record("recorded") is None
    worker.add(2, 3).result(timeout=1)
    assert worker.events == ["initialized", "recorded"]


def test_stop_can_be_queued_when_queue_is_full() -> None:
    worker = CommandQueueThread(max_queue_size=2)
    try:
        queued = worker.submit(lambda: None)

        with pytest.raises(Full):
            worker.submit(lambda: None)

        stopped = worker.stop()
        worker.start()
        worker.initialized.result(timeout=1)
        queued.result(timeout=1)
        stopped.result(timeout=1)
    finally:
        stopped = worker.stop()
        if worker.ident is None:
            worker.start()
        stopped.result(timeout=1)
        worker.join(timeout=1)
        assert not worker.is_alive()


# Main loop


def test_fire_and_forget_exception_does_not_stop_thread(
    worker: ExampleCommandQueueThread,
) -> None:
    assert worker.fail_fire_and_forget() is None
    assert worker.add(2, 3).result(timeout=1)[0] == 5


def test_command_exception_is_returned_without_stopping_thread(
    worker: ExampleCommandQueueThread,
) -> None:
    with pytest.raises(RuntimeError, match="command failed"):
        worker.fail().result(timeout=1)

    assert worker.add(2, 3).result(timeout=1)[0] == 5


@pytest.mark.parametrize("command_name", ["wait", "wait_and_fail"])
def test_cancelled_completion_does_not_stop_thread(
    worker: ExampleCommandQueueThread, command_name: str
) -> None:
    completion = getattr(worker, command_name)()
    assert completion.cancel()
    worker.release.set()

    assert worker.add(2, 3).result(timeout=1)[0] == 5


def test_idle_callback(worker: ExampleCommandQueueThread) -> None:
    assert worker.idle.wait(timeout=1)

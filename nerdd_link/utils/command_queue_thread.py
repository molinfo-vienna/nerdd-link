from collections import deque
from concurrent.futures import Future, InvalidStateError
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import wraps
from queue import Full
from threading import Condition, Lock, Thread
from typing import Any, Callable, Generic, Literal, Optional, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec

__all__ = ["CommandQueueThread", "command"]

ParamsT = ParamSpec("ParamsT")
CallbackParamsT = ParamSpec("CallbackParamsT")
ResultT = TypeVar("ResultT")
ThreadT = TypeVar("ThreadT", bound="CommandQueueThread")


@dataclass
class _Invocation(Generic[ResultT]):
    # The specification of the function to invoke (callable, args, kwargs).
    callback: Callable[..., ResultT]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    # The Future that will be completed when the command is finished. If None, the caller does
    # not care about the result of the command (fire-and-forget).
    completion: Optional[Future[ResultT]] = None


class _TerminateCommandQueue(BaseException):
    pass


class _LifecycleState(Enum):
    INITIALIZING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()


@overload
def command(
    method: Callable[Concatenate[ThreadT, ParamsT], ResultT],
    /,
) -> Callable[Concatenate[ThreadT, ParamsT], Future[ResultT]]: ...


@overload
def command(
    method: None = None,
    /,
    *,
    fire_and_forget: Literal[False] = False,
) -> Callable[
    [Callable[Concatenate[ThreadT, ParamsT], ResultT]],
    Callable[Concatenate[ThreadT, ParamsT], Future[ResultT]],
]: ...


@overload
def command(
    method: None = None,
    /,
    *,
    fire_and_forget: Literal[True],
) -> Callable[
    [Callable[Concatenate[ThreadT, ParamsT], Any]],
    Callable[Concatenate[ThreadT, ParamsT], None],
]: ...


def command(
    method: Optional[Callable[..., Any]] = None,
    /,
    *,
    fire_and_forget: bool = False,
) -> Any:
    def decorate(callback: Callable[..., Any]) -> Callable[..., Any]:
        # instead of calling the decorated method directly, enqueue it in the command queue
        @wraps(callback)
        def enqueue(thread: ThreadT, *args: Any, **kwargs: Any) -> Any:
            if fire_and_forget:
                return thread.submit_fire_and_forget(callback, thread, *args, **kwargs)
            return thread.submit(callback, thread, *args, **kwargs)

        return enqueue

    return decorate if method is None else decorate(method)


class CommandQueueThread(Thread):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        max_queue_size: int = 10_000,
        idle_timeout: float = 0.1,
    ) -> None:
        super().__init__(name=name)

        if max_queue_size <= 0:
            raise ValueError("max_queue_size must be greater than zero.")
        if idle_timeout <= 0:
            raise ValueError("idle_timeout must be greater than zero.")

        self._commands: deque[_Invocation[Any]] = deque()
        self._max_queue_size = max_queue_size
        self._idle_timeout = idle_timeout
        self._commands_available = Condition(Lock())
        self._lifecycle_state = _LifecycleState.INITIALIZING

        # for the special initialization and shutdown commands, we create separate futures
        self._initialization_future = self._run_initialization()
        self._shutdown_future: Optional[Future[None]] = None

    #
    # Initialization
    #
    @command
    def _run_initialization(self) -> None:
        try:
            self._initialize()
        except BaseException as error:
            raise _TerminateCommandQueue() from error

        with self._commands_available:
            # stop() may have been called while initialization was running.
            if self._lifecycle_state is _LifecycleState.INITIALIZING:
                self._lifecycle_state = _LifecycleState.RUNNING

    def _initialize(self) -> None:
        pass

    @property
    def initialized(self) -> Future[None]:
        return self._initialization_future

    #
    # Shutdown
    #
    def stop(self) -> Future[None]:
        with self._commands_available:
            if self._shutdown_future is not None:
                return self._shutdown_future
            if self._lifecycle_state is _LifecycleState.STOPPED:
                self._shutdown_future = Future()
                self._shutdown_future.set_result(None)
                return self._shutdown_future

            self._lifecycle_state = _LifecycleState.STOPPING
            completion: Future[None] = Future()
            self._shutdown_future = completion

            # stop command should always be queued and we don't check queue size here
            self._commands.append(_Invocation(self._run_shutdown, completion=completion))
            self._commands_available.notify()
            return completion

    def _run_shutdown(self) -> None:
        try:
            self._shutdown()
        except BaseException as error:
            raise _TerminateCommandQueue() from error
        raise _TerminateCommandQueue()

    def _shutdown(self) -> None:
        pass

    #
    # Submit tasks
    #
    def submit(
        self,
        callback: Callable[CallbackParamsT, ResultT],
        /,
        *args: CallbackParamsT.args,
        **kwargs: CallbackParamsT.kwargs,
    ) -> Future[ResultT]:
        completion: Future[ResultT] = Future()
        self._submit(_Invocation(callback, args, kwargs, completion))
        return completion

    def submit_fire_and_forget(
        self,
        callback: Callable[CallbackParamsT, Any],
        /,
        *args: CallbackParamsT.args,
        **kwargs: CallbackParamsT.kwargs,
    ) -> None:
        self._submit(_Invocation(callback, args, kwargs))

    def _submit(self, invocation: _Invocation[Any]) -> None:
        with self._commands_available:
            if self._lifecycle_state not in (
                _LifecycleState.INITIALIZING,
                _LifecycleState.RUNNING,
            ):
                raise RuntimeError("Cannot submit commands after shutdown has started.")
            if len(self._commands) >= self._max_queue_size:
                raise Full

            self._commands.append(invocation)
            self._commands_available.notify()

    #
    # Main loop
    #
    def run(self) -> None:
        termination_error: Optional[BaseException] = None
        try:
            while True:
                # get next command in queue (or run _on_idle)
                with self._commands_available:
                    if len(self._commands) == 0:
                        self._commands_available.wait(timeout=self._idle_timeout)

                    # after waiting, check if we have a command to run
                    command = self._commands.popleft() if len(self._commands) > 0 else None

                if command is None:
                    self._on_idle()
                    continue

                try:
                    # run command
                    result = command.callback(*command.args, **command.kwargs)
                except BaseException as error:
                    terminate = isinstance(error, _TerminateCommandQueue)
                    completion_error = error.__cause__ if terminate else error

                    if command.completion is not None:
                        if completion_error is None:
                            # command requests stop
                            self._set_result(command.completion, None)
                        else:
                            # command raised an exception
                            self._set_exception(command.completion, completion_error)

                    if terminate:
                        termination_error = completion_error
                        return
                else:
                    # We set the result outside of the try block so exceptions are not handled by
                    # the except block above.
                    if command.completion is not None:
                        self._set_result(command.completion, result)
        except BaseException as error:
            termination_error = error
            raise
        finally:
            with self._commands_available:
                self._lifecycle_state = _LifecycleState.STOPPED

                # copy the commands before clearing the queue
                pending = tuple(self._commands)

                self._commands.clear()

            for invocation in pending:
                if invocation.completion is not None:
                    pending_error = termination_error or RuntimeError(
                        "Command queue stopped before the command could run."
                    )
                    self._set_exception(invocation.completion, pending_error)

    def _on_idle(self) -> None:
        pass

    @staticmethod
    def _set_result(future: Future[ResultT], result: ResultT) -> None:
        try:
            future.set_result(result)
        except InvalidStateError:
            if not future.cancelled():
                raise

    @staticmethod
    def _set_exception(future: Future[Any], error: BaseException) -> None:
        try:
            future.set_exception(error)
        except InvalidStateError:
            if not future.cancelled():
                raise

from queue import Queue, SimpleQueue
from threading import Event, Thread
from typing import Any, Iterator, List

from nerdd_module.steps import OutputStep, Step

from ..utils import run_pipeline

__all__ = ["SplitAndMergeStep"]


class SplitAndMergeStep(OutputStep):
    def __init__(self, *step_lists: List[Step], queue_length: int = 10_000) -> None:
        super().__init__()

        for step_list in step_lists:
            if not isinstance(step_list[-1], OutputStep):
                raise TypeError("The last step in each step list must be an OutputStep.")

        if queue_length <= 0:
            raise ValueError("queue_length must be positive.")

        self._step_lists = step_lists
        self._queue_length = queue_length

    def _get_result(self, source: Iterator[dict]) -> None:
        # This pipeline step iterates through the source, copies all records in different queues
        # (for each branch in self._step_lists). In parallel, each branch in self._step_lists
        # consumes its queue and processes the records.
        queues: List[Queue[Any]] = [Queue(maxsize=self._queue_length) for _ in self._step_lists]

        # If any of the threads encounters an exception, it will be stored in exception_bucket. We
        # are only interested in the first error, but we use a queue here (instead of an ordinary
        # variable) to avoid race conditions.
        exception_bucket: SimpleQueue[BaseException] = SimpleQueue()

        # Each thread will put this end marker into its queue when all records have been processed.
        end = object()

        # If any of the threads encounters an exception, it will set this shared event.
        abort = Event()

        def _run_steps(steps: List[Step], queue: Queue[Any]) -> None:
            reached_end = False

            def queue_source() -> Iterator[dict]:
                nonlocal reached_end

                while True:
                    item = queue.get()

                    # end marker was reached
                    if item is end:
                        reached_end = True
                        return

                    if abort.is_set():
                        return

                    yield item

            try:
                run_pipeline(queue_source(), *steps)

                # It is possible to have reached_end = False without an error if run_pipeline()
                # stopped consuming.
                if not reached_end and not abort.is_set():
                    raise RuntimeError(
                        "A SplitAndMergeStep branch stopped before consuming all input."
                    )
            except BaseException as error:
                exception_bucket.put(error)
                abort.set()
            finally:
                # Keep consuming this branch's queue so that the producer cannot remain blocked
                # when the branch stops before reaching the end marker.
                if not reached_end:
                    while queue.get() is not end:
                        pass

        threads = [
            Thread(target=_run_steps, args=(steps, queue))
            for steps, queue in zip(self._step_lists, queues)
        ]

        for thread in threads:
            thread.start()

        # consume the source and copy all records to the different queues.
        try:
            for record in source:
                for queue in queues:
                    queue.put(record)

                if abort.is_set():
                    break
        except BaseException:
            abort.set()
            raise
        finally:
            # add the end marker to all queues
            for queue in queues:
                queue.put(end)

            for thread in threads:
                thread.join()

        # raise errors that occurred in the threads
        if not exception_bucket.empty():
            raise exception_bucket.get()

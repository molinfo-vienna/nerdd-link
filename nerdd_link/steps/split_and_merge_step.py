from functools import reduce
from itertools import tee
from queue import Queue
from threading import Barrier, Lock, Thread
from typing import Any, Callable, Iterator, List, cast

from nerdd_module import OutputStep, Step

__all__ = ["SplitAndMergeStep"]


class SplitAndMergeStep(OutputStep):
    def __init__(self, *step_lists: List[Step]) -> None:
        super().__init__()

        for step_list in step_lists:
            assert isinstance(
                step_list[-1], OutputStep
            ), "The last step in each step list must be an OutputStep."

        self._step_lists = step_lists

    def _get_result(self, source: Iterator[dict]) -> Any:
        # We make copies of the source iterator for each step list. If one of the step lists
        # consumes the source, the other step lists will still be able to consume it.
        source_copies = tee(source, len(self._step_lists))

        lock = Lock()
        barrier = Barrier(len(self._step_lists))

        def sync_step(source: Iterator[dict]) -> Iterator[dict]:
            while True:
                # Since itertools.tee is not thread-safe, we need to synchronize the access to the
                # source iterator with a lock.
                with lock:
                    try:
                        yield next(source)
                    except StopIteration:
                        break

                # We have to wait for all threads to finish processing the current item before
                # continuing, because one thread might be faster than the others.
                barrier.wait()

        # concatenate the steps to form pipelines
        for steps, source in zip(self._step_lists, source_copies):
            # put the sync step at the beginning of each step list
            synced_step_list: List[Callable[[Iterator[dict]], Iterator[dict]]] = [sync_step, *steps]

            # Concatenate the steps in each step list.
            # e.g. reduce(..., [step1, step2, step3], source)
            # --> step3(step2(step1(source)))
            reduce(lambda x, y: y(x), synced_step_list, source)

        for steps in self._step_lists:
            assert isinstance(
                steps[-1], OutputStep
            ), "The last step in each step list must be an OutputStep."

        output_steps = [cast(OutputStep, steps[-1]) for steps in self._step_lists]

        # When a thread throws an exception, it won't be caught by the main thread. That is why
        # we create an exception bucket and add the exceptions to it. The main thread will then
        # raise the first exception in the bucket.
        exception_bucket: Queue = Queue()

        def _run_steps(output_step: OutputStep) -> Any:
            try:
                return output_step.get_result()
            except Exception as e:
                exception_bucket.put(e)

        threads = [Thread(target=_run_steps, args=(output_step,)) for output_step in output_steps]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # raise errors that occurred in the threads
        if not exception_bucket.empty():
            raise exception_bucket.get()

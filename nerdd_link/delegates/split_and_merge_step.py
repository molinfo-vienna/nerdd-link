from functools import reduce
from queue import Queue
from threading import Thread
from typing import Any, Iterator, List

from nerdd_module import OutputStep, Step

from ..utils import safetee

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
        # Note: we use a thread-safe variant of tee.
        source_copies = safetee(source, len(self._step_lists))

        # When a thread throws an exception, it won't be caught by the main thread. That is why
        # we create an exception bucket and add the exceptions to it. The main thread will then
        # raise the first exception in the bucket.
        exception_bucket: Queue = Queue()

        def _run_steps(steps: List[Step], source: Iterator[dict]) -> Any:
            try:
                assert len(steps) > 0, "There must be at least one step."

                output_step = steps[-1]
                assert isinstance(output_step, OutputStep), "The last step must be an OutputStep."

                # Concatenate the steps in each step list.
                # e.g. step_list = [step1, step2, step3]
                # --> step3(step2(step1(source)))
                reduce(lambda x, y: y(x), steps, source)

                return output_step.get_result()
            except Exception as e:
                exception_bucket.put(e)

        threads = [
            Thread(target=_run_steps, args=(step_list, source_copy))
            for step_list, source_copy in zip(self._step_lists, source_copies)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # raise errors that occurred in the threads
        if not exception_bucket.empty():
            raise exception_bucket.get()

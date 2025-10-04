from typing import Any, Callable, Iterator, Optional, Union

from nerdd_module import OutputStep

__all__ = ["run_pipeline"]

StepLike = Callable[[Optional[Iterator[dict]]], Iterator[dict]]


def run_pipeline(first_step: Union[Iterator[dict], StepLike], *steps: StepLike) -> Any:
    # first step might be an iterator
    if isinstance(first_step, Iterator):
        pipeline = first_step
    else:
        pipeline = first_step(None)

    # build the pipeline from the list of steps
    for t in steps:
        pipeline = t(pipeline)

    # we will run the pipeline using the last step
    output_step = steps[-1]
    assert isinstance(output_step, OutputStep), "The last step must be an OutputStep."

    return output_step.get_result()

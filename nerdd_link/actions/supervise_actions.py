import asyncio
import logging
from typing import Dict, List, Optional

from .action import Action

__all__ = ["supervise_actions"]

logger = logging.getLogger(__name__)


async def supervise_actions(actions: List[Action], max_retries: Optional[int] = None) -> None:
    if max_retries is not None and max_retries < 0:
        raise ValueError("max_retries must be non-negative or None.")

    tasks: Dict[asyncio.Task, Action] = {}
    num_retries: Dict[Action, int] = {action: 0 for action in actions}

    def start_action(action: Action) -> None:
        logger.info("Running action %s", action)
        tasks[asyncio.create_task(action.run())] = action

    async def cancel_all_tasks() -> None:
        logger.info("Cancelling all running actions...")
        active_tasks = list(tasks.keys())
        for task in active_tasks:
            task.cancel()
        await asyncio.gather(*active_tasks, return_exceptions=True)
        tasks.clear()

    # start all actions
    for action in actions:
        start_action(action)

    try:
        while len(tasks) > 0:
            # wait until any task finishes (either successfully or with an exception)
            done_tasks, _ = await asyncio.wait(
                tasks.keys(),
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done_tasks:
                action = tasks.pop(task)

                # if the task was cancelled, then this happened via cancel_all_tasks()
                # -> don't restart the action
                if task.cancelled():
                    continue

                error = task.exception()

                # if the action stopped, there are multiple possibilities:
                # 1. the channel was stopped -> don't restart the action
                # 2. the action stopped due to an error or failed
                #    2a. max_retries limit not reached -> restart the action
                #    2b. max_retries limit reached -> cancel all actions and raise the error
                if not action.channel.is_running:
                    logger.info(
                        "Action %s finished while its channel was stopping. Not restarting.",
                        action,
                        exc_info=error,
                    )
                    continue
                elif max_retries is None or num_retries[action] < max_retries:
                    num_retries[action] += 1
                    if error is None:
                        logger.error(
                            "Action %s finished unexpectedly. Restarting... (%s/%s)",
                            action,
                            num_retries[action],
                            "inf" if max_retries is None else max_retries,
                        )
                    else:
                        logger.error(
                            "Action %s failed. Restarting... (%s/%s)",
                            action,
                            num_retries[action],
                            "inf" if max_retries is None else max_retries,
                            exc_info=error,
                        )
                    start_action(action)
                else:
                    logger.error(
                        "Action %s failed after %s retries",
                        action,
                        num_retries[action],
                        exc_info=error,
                    )
                    if error is None:
                        raise RuntimeError("Action finished unexpectedly")
                    else:
                        raise error
    finally:
        await cancel_all_tasks()

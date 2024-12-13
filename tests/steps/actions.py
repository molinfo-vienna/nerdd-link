import asyncio

import pytest_asyncio
from pytest_bdd import given, parsers, when

from nerdd_link.actions import (PredictCheckpointsAction, ProcessJobsAction,
                                RegisterModuleAction, SerializeJobAction)

from .async_step import async_step


@given(
    parsers.parse("the maximum number of molecules is {value:d}"),
    target_fixture="max_num_molecules",
)
def max_num_molecules(value):
    return value


@given(
    parsers.parse("the checkpoint size is {value:d}"), target_fixture="checkpoint_size"
)
def checkpoint_size(value):
    return value


@pytest_asyncio.fixture(scope="function")
async def process_job_action(channel, checkpoint_size, max_num_molecules, data_dir):
    action = ProcessJobsAction(
        channel=channel,
        max_num_molecules=max_num_molecules,
        checkpoint_size=checkpoint_size,
        data_dir=data_dir,
        num_test_entries=10,
        ratio_valid_entries=0.5,
        maximum_depth=50,
        max_num_lines_mol_block=10000,
    )

    task = asyncio.create_task(action.run())
    yield task
    task.cancel()


@when(parsers.parse("the process job action is executed"))
@async_step
async def execute_process_job_action(process_job_action):
    return process_job_action


@pytest_asyncio.fixture(scope="function")
async def predict_checkpoints_action(channel, model, data_dir):
    action = PredictCheckpointsAction(
        channel=channel,
        model=model,
        data_dir=data_dir,
    )

    task = asyncio.create_task(action.run())
    yield task
    task.cancel()


@when(parsers.parse("the predict checkpoints action is executed"))
@async_step
async def execute_predict_checkpoints_action(predict_checkpoints_action):
    return predict_checkpoints_action


@pytest_asyncio.fixture(scope="function")
async def register_module_action(channel, model):
    action = RegisterModuleAction(
        channel=channel,
        model=model,
    )

    task = asyncio.create_task(action.run())
    yield task
    task.cancel()


@when(parsers.parse("the register module action is executed"))
@async_step
async def execute_register_module_action(register_module_action):
    return register_module_action


@pytest_asyncio.fixture(scope="function")
async def serialize_job_action(channel, model, data_dir):
    action = SerializeJobAction(
        channel=channel,
        model=model,
        data_dir=data_dir,
    )

    task = asyncio.create_task(action.run())
    yield task
    task.cancel()


@when(parsers.parse("the serialize job action is executed"))
@async_step
async def execute_serialize_job_action(serialize_job_action):
    return serialize_job_action
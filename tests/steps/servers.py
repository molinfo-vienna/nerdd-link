import asyncio

import pytest_asyncio
from pytest_bdd import parsers, when

from nerdd_link.cli.run_job_server import _run_job_server
from nerdd_link.cli.run_prediction_server import _run_prediction_server
from nerdd_link.cli.run_serialization_server import _run_serialization_server
from nerdd_link.tests import async_step


@pytest_asyncio.fixture(scope="function")
async def prediction_server(model, channel, data_dir):
    task = asyncio.create_task(
        _run_prediction_server(
            model=model,
            channel=channel,
            data_dir=data_dir,
        )
    )
    yield task
    task.cancel()


@when(parsers.parse("the prediction server is running"))
@async_step
async def execute_prediction_server(prediction_server):
    return prediction_server


@pytest_asyncio.fixture(scope="function")
async def job_server(channel, data_dir):
    task = asyncio.create_task(
        _run_job_server(
            channel=channel,
            num_test_entries=10,
            ratio_valid_entries=0.5,
            maximum_depth=50,
            max_num_lines_mol_block=10000,
            data_dir=data_dir,
        )
    )
    yield task
    task.cancel()


@when(parsers.parse("the job server is running"))
@async_step
async def execute_job_server(job_server):
    return job_server


@pytest_asyncio.fixture(scope="function")
async def serialization_server(channel, data_dir):
    task = asyncio.create_task(
        _run_serialization_server(
            channel=channel,
            data_dir=data_dir,
        )
    )
    yield task
    task.cancel()


@when(parsers.parse("the serialization server is running"))
@async_step
async def execute_serialization_server(serialization_server):
    return serialization_server

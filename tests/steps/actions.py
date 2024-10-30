from tempfile import TemporaryDirectory

from nerdd_link.actions import (
    PredictCheckpointsAction,
    ProcessJobsAction,
    RegisterModuleAction,
)
from pytest_bdd import given, parsers, when


@given("the data directory is a temporary directory", target_fixture="data_dir")
def data_dir():
    with TemporaryDirectory() as temp_dir:
        yield temp_dir


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


@when(parsers.parse("the process job action is executed"))
def execute_process_job_action(channel, checkpoint_size, max_num_molecules, data_dir):
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

    action.start()
    # wait for the action to finish
    # (this will happen, because the number of messages in the queue is finite)
    action.join()


@when(parsers.parse("the predict checkpoints action is executed"))
def execute_predict_checkpoints_action(channel, model, data_dir):
    action = PredictCheckpointsAction(
        channel=channel,
        model=model,
        data_dir=data_dir,
    )

    action.start()
    # wait for the action to finish
    # (this will happen, because the number of messages in the queue is finite)
    action.join()


@when(parsers.parse("the register module action is executed"))
def register_module_action(channel, model):
    action = RegisterModuleAction(
        channel=channel,
        model=model,
    )

    action.start()
    # wait for the action to finish
    # (this will happen, because the number of messages in the queue is finite)
    action.join()

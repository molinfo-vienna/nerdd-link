import os

from nerdd_module import ReadInputStep, WriteOutputStep
from nerdd_module.input import DepthFirstExplorer
from pytest_bdd import given, parsers, then


@given(parsers.parse("a file '{path}' with the molecules in format '{format}'"))
def input_file(data_dir, path, molecules, format):
    # the path is relative to the data directory
    full_path = os.path.join(data_dir, path)

    # create the directory if it does not exist
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    explorer = DepthFirstExplorer(
        data_dir=os.path.join(data_dir, "sources"),
    )

    input_step = ReadInputStep(explorer, molecules)
    output_step = WriteOutputStep(output_format=format, output_file=full_path)
    output_step(input_step(None))
    output_step.get_result()


@then(parsers.parse("the file '{path}' is created"))
def file_created(data_dir, path):
    full_path = os.path.join(data_dir, path)
    assert os.path.exists(full_path)

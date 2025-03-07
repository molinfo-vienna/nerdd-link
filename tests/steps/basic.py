import asyncio
import os

from nerdd_module import ReadInputStep, WriteOutputStep
from nerdd_module.config import Module
from nerdd_module.input import DepthFirstExplorer
from pytest_bdd import given, parsers, then, when

from nerdd_link.tests import async_step


@given(parsers.parse("a file '{path}' with the molecules in format '{format}'"))
def input_file(data_dir, path, molecules, format):
    # the path is relative to the data directory
    full_path = os.path.join(data_dir, path)

    # create the directory if it does not exist
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    explorer = DepthFirstExplorer(
        data_dir=os.path.join(data_dir, "sources"),
    )

    # When reading the input file, we get entries of the form
    # { "input_mol": <molecule>, "raw_input": "CCCO", "input_type": "smiles", etc. }
    # We remove all properties except "input_mol", because we don't want to store them.
    def remove_properties(source):
        for entry in source:
            yield { "input_mol": entry["input_mol"] }

    input_step = ReadInputStep(explorer, molecules)
    output_step = WriteOutputStep(config=Module(name="dummy"), output_format=format, output_file=full_path)
    output_step(remove_properties(input_step(None)))
    output_step.get_result()


@then(parsers.parse("the file '{path}' is created"))
def file_created(data_dir, path):
    full_path = os.path.join(data_dir, path)
    assert os.path.exists(full_path)


@when(parsers.parse("we wait for {seconds:d} seconds"))
@async_step
async def wait_for_seconds(seconds):
    await asyncio.sleep(seconds)

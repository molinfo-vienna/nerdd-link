from tempfile import TemporaryDirectory

from pytest_bdd import given


@given("a temporary data directory", target_fixture="data_dir")
def data_dir():
    with TemporaryDirectory() as temp_dir:
        yield temp_dir

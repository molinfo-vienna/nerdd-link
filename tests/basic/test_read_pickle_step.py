import pickle

from nerdd_link.polyfills import SpooledTemporaryFile
from nerdd_link.steps import ReadPickleStep


def test_reads_a_spooled_temporary_file() -> None:
    # this would fail on Python 3.9 and its version of SpooledTemporaryFile
    with SpooledTemporaryFile(mode="w+b") as file_handle:
        pickle.dump([{"id": "record-1"}], file_handle)
        file_handle.seek(0)

        assert list(ReadPickleStep(file_handle)._run()) == [{"id": "record-1"}]

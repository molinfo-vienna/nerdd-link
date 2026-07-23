import tempfile

from nerdd_link.output import PickleWriter


def test_unpicklable_values():
    with tempfile.NamedTemporaryFile() as temp_file:
        pickle_writer = PickleWriter(temp_file)

        # temp_file is a _io.BufferedRandom object that cannot be pickled
        # pickle_writer should not raise an error
        pickle_writer.write([{"file": temp_file}])

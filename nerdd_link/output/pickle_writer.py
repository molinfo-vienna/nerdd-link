import pickle
from typing import IO, Any, Iterable

from nerdd_module.output import FileLike, FileWriter, WriterConfig
from rdkit.Chem import Mol
from rdkit.Chem.PropertyMol import PropertyMol

__all__ = ["PickleWriter"]


class PickleWriter(FileWriter):
    def __init__(self, output_file: FileLike) -> None:
        super().__init__(output_file, writes_bytes=True)

    def _write(self, output: IO[Any], entries: Iterable[dict]) -> None:
        results = []

        #
        # replace values that can not be pickled
        #
        REPLACEMENT = None

        # create a whitelist for types that are known to be picklable
        whitelist = (str, int, float, bool, PropertyMol, Mol)

        # check entries and replace
        def _check_entry(entry: dict) -> dict:
            for key, value in entry.items():
                if value is None or isinstance(value, whitelist):
                    continue

                # try to pickle the value
                try:
                    pickle.dumps(value)
                except Exception:
                    entry[key] = REPLACEMENT

            return entry

        results = [_check_entry(entry) for entry in entries]

        pickle.dump(results, output)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(output_file='{self._output_file}')"

    config = WriterConfig(output_format="pickle")

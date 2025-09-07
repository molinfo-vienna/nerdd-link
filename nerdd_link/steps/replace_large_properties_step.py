from typing import Any, Iterator, Optional

from nerdd_module import Step
from nerdd_module.config import Module

from ..files import FileSystem

__all__ = ["ReplaceLargePropertiesStep"]


class ReplaceLargePropertiesStep(Step):
    def __init__(
        self,
        config: Module,
        file_system: FileSystem,
        job_id: str,
    ) -> None:
        super().__init__()
        self._file_system = file_system
        self._job_id = job_id

        # large properties
        self._large_properties = [
            p.name for p in config.result_properties if p.type in ["image", "mol"]
        ]

        # molecular properties
        self._molecular_properties = [
            p.name for p in config.result_properties if p.level is None or p.level == "molecule"
        ]

    def _process_property(self, record: dict, record_id: str, sub_id: Optional[str], k: str) -> Any:
        v = record[k]

        # never store None in a file
        if v is None:
            return None

        # only store large properties on disk
        if k not in self._large_properties:
            return v

        #
        # store large properties (images, molecules) on disk
        #

        # we store molecular properties exactly once and reference them in sub records
        # -> if the property is a molecular property, we store the value in <mol_id>
        #    and otherwise in <mol_id>-<sub_id>
        if k in self._molecular_properties:
            file_path = self._file_system.get_property_file_path(
                job_id=self._job_id, property_name=k, record_id=str(record["mol_id"])
            )
        else:
            file_path = self._file_system.get_property_file_path(
                job_id=self._job_id, property_name=k, record_id=record_id
            )

        # write the property to a file
        # case 1: atomic or derivative properties (k not in self._molecular_properties)
        # case 2: molecular properties in molecular property prediction (sub_id = None)
        # case 3: molecular properties in atom / derivative property prediction (sub_id = 0)
        if k not in self._molecular_properties or sub_id is None or sub_id == 0:
            with open(file_path, "wb") as f:
                if isinstance(v, bytes):
                    f.write(v)
                else:
                    f.write(str(v).encode("utf-8"))

        return f"file://{file_path}"

    def _run(self, source: Iterator[dict]) -> Iterator[dict]:
        for record in source:
            if "atom_id" in record:
                record_id = f"{record['mol_id']}-{record['atom_id']}"
                sub_id = record["atom_id"]
            elif "derivative_id" in record:
                record_id = f"{record['mol_id']}-{record['derivative_id']}"
                sub_id = record["derivative_id"]
            else:
                record_id = str(record["mol_id"])
                sub_id = None

            modified_record = {
                k: self._process_property(record, record_id, sub_id, k) for k in record.keys()
            }

            yield modified_record

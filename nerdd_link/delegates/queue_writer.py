from asyncio import AbstractEventLoop, Queue, run_coroutine_threadsafe
from typing import Any, Iterable

from nerdd_module import Writer, WriterConfig
from nerdd_module.config import Module

from ..files import FileSystem

__all__ = ["QueueWriter"]


class QueueWriter(Writer):
    def __init__(
        self,
        config: Module,
        queue: Queue,
        loop: AbstractEventLoop,
        file_system: FileSystem,
        job_id: str,
    ) -> None:
        super().__init__()
        self._queue = queue
        self._loop = loop
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

    def _replace_properties(self, record: dict) -> dict:
        """
        Replace large properties in the record with file paths.
        """
        if "atom_id" in record:
            record_id = f"{record['mol_id']}-{record['atom_id']}"
            sub_id = record["atom_id"]
        elif "derivative_id" in record:
            record_id = f"{record['mol_id']}-{record['derivative_id']}"
            sub_id = record["derivative_id"]
        else:
            record_id = str(record["mol_id"])
            sub_id = None

        def _r(k: str) -> Any:
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

        return {k: _r(k) for k, v in record.items()}

    def write(self, records: Iterable[dict]) -> None:
        job_id = self._job_id
        for record in records:
            # store large properties (images, molecules) on disk
            modified_record = self._replace_properties(record)

            # generate an id for the result
            mol_id = record["mol_id"]
            if "atom_id" in modified_record:
                atom_id = record["atom_id"]
                id = f"{job_id}-{mol_id}-{atom_id}"
            elif "derivative_id" in record:
                derivative_id = record["derivative_id"]
                id = f"{job_id}-{mol_id}-{derivative_id}"
            else:
                id = f"{job_id}-{mol_id}"

            modified_record["id"] = id

            run_coroutine_threadsafe(self._queue.put(modified_record), self._loop)

        run_coroutine_threadsafe(self._queue.put(None), self._loop)

    config = WriterConfig(output_format="json")

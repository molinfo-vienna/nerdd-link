from asyncio import AbstractEventLoop, Queue, run_coroutine_threadsafe
from typing import Any, Iterable

from nerdd_module import Writer, WriterConfig
from nerdd_module.config import Module

from ..files import FileSystem

__all__ = ["TopicWriter"]


class TopicWriter(Writer):
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

    def _replace_property(self, record_id: str, property_name: str, property_value: Any) -> str:
        """
        Replace large properties with file paths.
        """
        if property_value is None:
            return None

        # store large properties (images, molecules) on disk
        file_path = self._file_system.get_property_file_path(
            job_id=self._job_id, property_name=property_name, record_id=record_id
        )
        with open(file_path, "wb") as f:
            f.write(str(property_value).encode("utf-8"))

        return f"file://{file_path}"

    def _replace_properties(self, record: dict) -> dict:
        """
        Replace large properties in the record with file paths.
        """
        if "atom_id" in record:
            record_id = f"{record['mol_id']}-{record['atom_id']}"
        elif "derivative_id" in record:
            record_id = f"{record['mol_id']}-{record['derivative_id']}"
        else:
            record_id = str(record["mol_id"])

        return {
            k: self._replace_property(record_id, k, v) if k in self._large_properties else v
            for k, v in record.items()
        }

    def write(self, records: Iterable[dict]) -> None:
        for record in records:
            # store large properties (images, molecules) on disk
            modified_record = self._replace_properties(record)

            run_coroutine_threadsafe(self._queue.put(modified_record), self._loop)

        run_coroutine_threadsafe(self._queue.put(None), self._loop)

    config = WriterConfig(output_format="json")

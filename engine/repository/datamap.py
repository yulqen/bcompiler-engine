from pathlib import Path

from ..use_cases.parsing import datamap_reader


class InMemorySingleDatamapRepository:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def list_as_objs(self):
        return datamap_reader(self.filepath)

from pathlib import Path

from ..serializers.datamap import datamap_json_serializer
from ..use_cases.parsing import datamap_reader


class InMemorySingleDatamapRepository:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def list_as_objs(self):
        return datamap_reader(self.filepath)

    def list_as_json(self):
        lst_of_objs = datamap_reader(self.filepath)
        return datamap_json_serializer(lst_of_objs)

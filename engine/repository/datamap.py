from pathlib import Path

from ..serializers.datamap import datamap_json_serializer
from ..use_cases.parsing import datamap_reader


class InMemorySingleDatamapRepository:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def list_as_json(self):
        "Return list of DatamapLine objects parsed from filepath as json."
        lst_of_objs = datamap_reader(self.filepath)
        return datamap_json_serializer(lst_of_objs)

    def list_as_objs(self):
        "Return list of DatamapLine objects parsed from filepath."
        return datamap_reader(self.filepath)

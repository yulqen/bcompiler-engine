import json
from pathlib import Path

from ..serializers.datamap import DatamapEncoder
from ..use_cases.parsing import datamap_reader


class InMemorySingleDatamapRepository:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def list_as_json(self):
        "Return list of DatamapLine objects parsed from filepath as json."
        lst_of_objs = datamap_reader(self.filepath)
        return json.dumps(lst_of_objs, cls=DatamapEncoder)

    def list_as_objs(self):
        "Return list of DatamapLine objects parsed from filepath."
        return datamap_reader(self.filepath)

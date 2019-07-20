import json
from typing import List

from ..domain.datamap import DatamapLine
from ..serializers.datamap import DatamapEncoder
from ..use_cases.parsing import datamap_reader


class InMemorySingleDatamapRepository:
    def __init__(self, directory_path: str):
        self.directory_path = directory_path

    def list_as_json(self) -> str:
        "Return list of DatamapLine objects parsed from filepath as json."
        lst_of_objs = datamap_reader(self.directory_path)
        return json.dumps(lst_of_objs, cls=DatamapEncoder)

    def list_as_objs(self) -> List[DatamapLine]:
        "Return list of DatamapLine objects parsed from filepath."
        return datamap_reader(self.directory_path)

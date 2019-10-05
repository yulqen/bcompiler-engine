import json
from pathlib import Path
from typing import List, Union

from engine.utils.extraction import datamap_reader

from ..domain.datamap import DatamapLine
from ..serializers.datamap import DatamapEncoder


class InMemorySingleDatamapRepository:
    def __init__(self, directory_path: Union[Path, str]):
        self.directory_path = str(directory_path)

    def list_as_json(self) -> str:
        "Return list of DatamapLine objects parsed from filepath as json."
        lst_of_objs = datamap_reader(self.directory_path)
        return json.dumps(lst_of_objs, cls=DatamapEncoder)

    def list_as_objs(self) -> List[DatamapLine]:
        "Return list of DatamapLine objects parsed from filepath."
        return datamap_reader(self.directory_path)

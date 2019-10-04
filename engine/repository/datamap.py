from typing import Union

from pathlib import Path

import json
from typing import List

from ..domain.datamap import DatamapLine
from ..serializers.datamap import DatamapEncoder
from engine.utils.extraction import datamap_reader


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

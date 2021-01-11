import json
from pathlib import Path
from typing import Dict, List, Union

from engine.utils.extraction import datamap_reader, max_tmpl_row

from ..domain.datamap import DatamapLine
from ..exceptions import DatamapNotCSVException
from ..serializers.datamap import DatamapEncoder


class InMemorySingleDatamapRepository:
    def __init__(self, datamap_path: Union[Path, str]) -> None:
        self.datamap_path = datamap_path
        self.row_limits: Dict[str, int] = max_tmpl_row(Path(datamap_path))

    def list_as_json(self) -> str:
        """Return list of DatamapLine objects parsed from filepath as json."""
        try:
            lst_of_objs = datamap_reader(self.datamap_path)
        except DatamapNotCSVException:
            raise
        return json.dumps(lst_of_objs, cls=DatamapEncoder)

    def list_as_objs(self) -> List[DatamapLine]:
        """Return list of DatamapLine objects parsed from filepath."""
        return datamap_reader(self.datamap_path)

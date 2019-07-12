import json
from typing import List

from engine.domain.datamap import DatamapLine


def datamap_json_serializer(lst_of_datamap_objs: List[DatamapLine]):
    return json.dumps([dml.to_dict() for dml in lst_of_datamap_objs])

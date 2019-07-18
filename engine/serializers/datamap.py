import json
from typing import Any


class DatamapEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any: # type: ignore
        try:
            to_serialize = {
                "key": o.key,
                "sheet": o.sheet,
                "cellref": o.cellref,
                "data_type": o.data_type,
                "filename": o.filename,
            }
            return to_serialize
        except AttributeError:
            return super().default(o)

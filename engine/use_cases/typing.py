from typing import List, NamedTuple


class ColData(NamedTuple):
    key: str
    sheet: str
    cellref: str
    value: str
    file_name: str


MASTER_COL_DATA = List[ColData]
MASTER_DATA_FOR_FILE = List[MASTER_COL_DATA]

from dataclasses import dataclass
from enum import Enum, auto
"""
The meat of new bcompiler.
"""


class DatamapLineValueType(Enum):
    NUMBER = auto()
    TEXT = auto()
    DATE = auto()


@dataclass
class DatamapLine:
    key: str
    sheet: str
    cellref: str
    data_type: str

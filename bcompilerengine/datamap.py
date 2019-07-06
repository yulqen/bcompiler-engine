"""
The meat of new bcompiler.
"""

from enum import Enum


class DatamapValueType(Enum):
    TEXT = 1
    INTEGER = 2
    FLOAT = 3
    DATE = 4


class DatamapLine:
    def __init__(self, key: str, sheet: str, cellref: str, data_type: DatamapValueType):
        self.key = key
        self.sheet = sheet
        self.cellref = cellref
        self.data_type = data_type

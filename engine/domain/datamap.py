"""
Entities relating to the datamap.
"""
from dataclasses import dataclass
from enum import Enum, auto


class DatamapLineValueType(Enum):
    """A representation of a data type for us in validating data from the spreadsheet.

    These are used in datamap processing and spreadsheet parsing to represent the
    type of data being extracted.
    """

    NUMBER = auto()
    TEXT = auto()
    DATE = auto()


class DatamapLine:
    """The core data structure that is configured by the user datamap.csv.

    Data structure representing all cell data extracted from templates/spreadsheets.
    """

    def __init__(self, key, sheet, cellref, data_type, filename):

        self.key = key
        self.sheet = sheet
        self.cellref = cellref
        self.data_type = data_type
        self.filename = filename

    def to_dict(self):
        return {
            "key": self.key,
            "sheet": self.sheet,
            "cellref": self.cellref,
            "data_type": self.data_type,
            "filename": self.filename,
        }
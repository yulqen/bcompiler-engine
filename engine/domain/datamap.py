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


@dataclass
class DatamapLine:
    """The core data structure that is configured by the user datamap.csv.

    Data structure representing all cell data extracted from templates/spreadsheets.
    """

    key: str
    sheet: str
    cellref: str
    data_type: str
    filename: str

"Entities relating to the datamap."
from enum import Enum, auto
from typing import Dict

# pylint: disable=R0903,R0913;


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

    def __init__(self, key: str, sheet: str, cellref: str, data_type: str,
                 filename: str) -> None:

        self.key = key
        self.sheet = sheet
        self.cellref = cellref
        self.data_type = data_type
        self.filename = filename

    def to_dict(self) -> Dict[str, str]:
        "Return the attributes as a dictionary."
        return {
            "key": self.key,
            "sheet": self.sheet,
            "cellref": self.cellref,
            "data_type": self.data_type,
            "filename": self.filename,
        }

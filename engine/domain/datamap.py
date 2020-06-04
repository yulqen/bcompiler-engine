"Entities relating to the datamap."
from enum import Enum, auto
from pathlib import Path

# pylint: disable=R0903,R0913;
from typing import IO, Dict, Optional, Union

from engine.exceptions import DatamapNotCSVException


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

    def __init__(
        self,
        key: str,
        sheet: str,
        cellref: str,
        data_type: Optional[str],
        filename: str,
    ) -> None:
        self.key = key
        self.sheet = sheet
        self.cellref = cellref
        self.data_type = data_type
        self.filename = filename

    def to_dict(self) -> Dict[str, Optional[str]]:
        "Return the attributes as a dictionary."
        return {
            "key": self.key,
            "sheet": self.sheet,
            "cellref": self.cellref,
            "data_type": self.data_type,
            "filename": self.filename,
        }


class DatamapFile:
    """A context manager that represents the datamap file.

    Having a context manager means we can more elegantly capture the
    exception with the file isn't found.
    """

    def __init__(self, filepath: Union[Path, str]) -> None:
        "Create the context manager"
        self.filepath = filepath

    def __enter__(self) -> IO[str]:
        try:
            # first check - is it a CSV file?
            # Note: that you are able to pass in Path objects here as well as str paths.
            try:
                _ext = f".{self.filepath.rpartition('.')[-1]}"  # type: ignore
            except AttributeError:
                _ext = self.filepath.suffix  # type: ignore
            if _ext != ".csv":
                raise DatamapNotCSVException("Given datamap file is not in CSV format.")
            self.f_obj = open(self.filepath, "r", encoding="utf-8")
            self.f_obj.read()
            self.f_obj.seek(0)
            return self.f_obj
        except DatamapNotCSVException:
            raise
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find {}".format(self.filepath))
        except UnicodeDecodeError:
            self.f_obj = open(self.filepath, "r", encoding="latin1")
            return self.f_obj

    def __exit__(self, mytype, value, traceback):  # type: ignore
        self.f_obj.close()

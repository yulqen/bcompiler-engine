"""
The domain object representing a populated "template", or a spreadsheet
containing data that we wish to extract.
"""
from typing import Dict

from .datamap import DatamapLineValueType  # noqa


class TemplateCell:
    "Used for collecting data from a populated spreadsheet."

    def __init__(
            self,
            file_name: str,
            sheet_name: str,
            cellref: str,
            value: str,
            data_type: DatamapLineValueType,
    ) -> None:
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.cellref = cellref
        self.value = value
        self.data_type = data_type

    def to_dict(self) -> Dict[str, str]:
        return {
            "file_name": self.file_name,
            "sheet_name": self.sheet_name,
            "cellref": self.cellref,
            "value": self.value,
            "data_type": self.data_type.name,
        }

"""
The domain object representing a populated "template", or a spreadsheet
containing data that we wish to extract.
"""
from dataclasses import dataclass

from .datamap import DatamapLineValueType  # noqa


@dataclass
class TemplateCell:
    """
    Used for collecting data from a populated spreadsheet.
    """

    file_name: str
    sheet_name: str
    cell_ref: str
    value: str
    data_type: DatamapLineValueType

import csv
import datetime
import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from openpyxl import load_workbook

from engine.datamap import DatamapLine, DatamapLineValueType


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


def get_cell_data(data: List[TemplateCell], sheet_name: str,
                  cell_ref: str) -> Optional[TemplateCell]:
    """
    Given a list of TemplateCell items, a sheet name and a cell reference,
    return a single TemplateCell object.
    """
    data_from_cell = [
        cell for cell in data
        if cell.sheet_name == sheet_name and cell.cell_ref == cell_ref
    ]
    if data_from_cell:
        return data_from_cell[0]
    else:
        raise RuntimeError(
            "There should never be more than one value for that sheet/cell combination"
        )


def clean(target_str: str, is_cell_ref: bool = False):
    """
    Rids a string of its most common problems: spacing, capitalisation,etc.
    """
    if not isinstance(target_str, str):
        raise TypeError("Can only clean a string.")
    output_str = target_str.lstrip().rstrip()
    if is_cell_ref:
        output_str = output_str.upper()
    return output_str


def datamap_reader(dm_file: str) -> List[DatamapLine]:
    """
    Given a datamap csv file, returns a list of DatamapLine objects.
    """
    data = []
    with open(dm_file, encoding="utf-8") as datamap_file:
        reader = csv.DictReader(datamap_file)
        for line in reader:
            data.append(
                DatamapLine(
                    key=clean(line["cell_key"]),
                    sheet=clean(line["template_sheet"]),
                    cellref=clean(line["cell_reference"], is_cell_ref=True),
                    data_type=clean(line["type"]),
                    filename=dm_file,
                ))
    return data


def template_reader(template_file: str) -> List[TemplateCell]:
    """
    Given a populated xlsx file, returns all data in a list of
    TemplateCell objects.
    """
    data = []
    workbook = load_workbook(template_file, data_only=True)
    for sheet in workbook.worksheets:
        for row in sheet.rows:
            for cell in row:
                if cell.value is not None:
                    try:
                        val = cell.value.rstrip().lstrip()
                        c_type = DatamapLineValueType.TEXT
                    except AttributeError:
                        if isinstance(cell.value, (float, int)):
                            val = cell.value
                            c_type = DatamapLineValueType.NUMBER
                        elif isinstance(cell.value,
                                        (datetime.date, datetime.datetime)):
                            val = cell.value
                            c_type = DatamapLineValueType.DATE
                    cell_ref = f"{cell.column_letter}{cell.row}"
                    tc = TemplateCell(template_file, sheet.title, cell_ref,
                                      val, c_type)
                    data.append(tc)
    return data


def get_xlsx_files(directory: Path) -> List[Path]:
    """
    Return a list of Path objects for each xlsx file in directory,
    or raise an exception.
    """
    output = []
    if not os.path.isabs(directory):
        raise RuntimeError("Require absolute path here")
    for file_path in os.listdir(directory):
        if fnmatch.fnmatch(file_path, "*.xlsx"):
            output.append(Path(os.path.join(directory, file_path)))
    return output

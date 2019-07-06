import csv
import datetime
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from openpyxl import load_workbook


class DatamapLineType(Enum):
    NUMBER = auto()
    STRING = auto()
    DATE = auto()


@dataclass
class TemplateCell:
    file_name: str
    sheet_name: str
    cell_ref: str
    value: str
    cell_type: DatamapLineType


def get_cell_data(data: List[TemplateCell], sheet_name: str,
                  cell_ref: str) -> Optional[TemplateCell]:
    """
    Given a list of TemplateCell items, a sheet name and a cell reference,
    return a single TemplateCell object.
    """
    tc = [
        cell for cell in data
        if cell.sheet_name == sheet_name and cell.cell_ref == cell_ref
    ]
    if tc:
        return tc[0]
    elif len(tc) > 1:
        raise RuntimeError(
            "There should never be more than one value for that sheet/cell combination"
        )
        sys.exit(1)
    else:
        return None


def datamap_reader(dm_file: str):
    with open(dm_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line in reader:
            print(line["key"])


def template_reader(template_file: str):
    data = []
    wb = load_workbook(template_file, data_only=True)
    for sheet in wb.worksheets:
        for row in sheet.rows:
            for cell in row:
                if cell.value is not None:
                    try:
                        val = cell.value.rstrip().lstrip()
                        c_type = DatamapLineType.STRING
                    except AttributeError:
                        if isinstance(cell.value, (float, int)):
                            val = cell.value
                            c_type = DatamapLineType.NUMBER
                        elif isinstance(cell.value,
                                        (datetime.date, datetime.datetime)):
                            val = cell.value
                            c_type = DatamapLineType.DATE
                    cell_ref = f"{cell.column_letter}{cell.row}"
                    tc = TemplateCell(template_file, sheet.title, cell_ref,
                                      val, c_type)
                    data.append(tc)
    return data


if __name__ == "__main__":
    TEMPLATE_FILE = "/home/lemon/Documents/bcompiler/template.xlsx"
    data = template_reader(TEMPLATE_FILE)

    for cell in range(200):
        print(data[cell])

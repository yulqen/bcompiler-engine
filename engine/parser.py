"""
Mostly, this module is about organising the main data structure.

Given a list of files and a dataset (a list of list of TemplateCell
objects - will return a dict of the form:

    dataset = {
    "test_template.xlsx": {
    "checksum": "fjfj34jk22l134hl",
    "data": {
        "Summary": {
            "A1": TemplateCell(file_name=PosixPath(..),
            "A2": TemplateCell(file_name=PosixPath(..),
            "A2": TemplateCell(file_name=PosixPath(..),
        },
        "Finances": {
            "A1": TemplateCell(file_name=PosixPath(..),
            "A4": TemplateCell(file_name=PosixPath(..),
            "A10": TemplateCell(file_name=PosixPath(..),
        }
    "test_template2.xlsx": {
    "checksum": "AFfjdddfa4jk134hl",
    "data": {
        "Summary": {
            "A1": TemplateCell(file_name=PosixPath(..),
            "A2": TemplateCell(file_name=PosixPath(..),
            "A2": TemplateCell(file_name=PosixPath(..),
        },
        "Finances": {
            "A1": TemplateCell(file_name=PosixPath(..),
            "A4": TemplateCell(file_name=PosixPath(..),
            "A10": TemplateCell(file_name=PosixPath(..),
        }
    }
"""
import csv
import datetime
import fnmatch
import hashlib
import os
from concurrent import futures
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, List, Optional

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


def get_cell_data(filepath: Path, data: List[TemplateCell], sheet_name: str,
                  cell_ref: str) -> Optional[TemplateCell]:
    """
    Given a list of TemplateCell items, a sheet name and a cell reference,
    return a single TemplateCell object.
    """
    _file_data = data[filepath.name]["data"]
    return _file_data[sheet_name][cell_ref]


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


def template_reader(template_file: str) -> Dict:
    """
    Given a populated xlsx file, returns all data in a list of
    TemplateCell objects.
    """
    inner_dict = {"data": {}}
    data = []
    f_path = Path(template_file)
    print(f"EXTRACTING FROM: {template_file}")
    workbook = load_workbook(template_file, data_only=True)
    checksum = hash_single_file(f_path)
    holding = []
    for sheet in workbook.worksheets:
        data_dict = {}
        sheet_data = []
        sheet_dict = {}
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
                    sheet_data.append(tc)
        sheet_dict.update({sheet.title: _extract_cellrefs(sheet_data)})
        holding.append(sheet_dict)
    for sd in holding:
        inner_dict["data"].update(sd)
    inner_dict.update({"checksum": checksum})
    shell_dict = {f_path.name: inner_dict}
    return shell_dict


def get_xlsx_files(directory: Path) -> List[Path]:
    """
    Return a list of Path objects for each xlsx file in directory,
    or raise an exception.
    """
    output = []
    if not os.path.isabs(directory):
        raise RuntimeError("Require absolute path here")
    for file_path in os.listdir(directory):
        if fnmatch.fnmatch(file_path, "*.xls[xm]"):
            output.append(Path(os.path.join(directory, file_path)))
    return output


# here is the version with out multiprocessing
# def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> set:
#    data = []
#    for file in map(template_reader, xlsx_files):
#        data.append(file)
#    return data


def _extract_sheets(lst_of_tcs: List[TemplateCell]
                    ) -> Dict[str, List[TemplateCell]]:
    output: Dict[str, List[TemplateCell]] = {}
    data = sorted(lst_of_tcs, key=lambda x: x.sheet_name)
    for k, g in groupby(data, key=lambda x: x.sheet_name):
        output.update({k: list(g)})
    return output


def _extract_cellrefs(lst_of_tcs: List[TemplateCell]
                      ) -> Dict[str, TemplateCell]:
    """Extract value from TemplateCell.cell_ref for each TemplateCell in a list to group them.

    When given a list of TemplateCell objects, this function extracts each TemplateCell
    by it's cell_ref value and groups them according. In the curent implementation, this is
    only called on a list of TemplateCell objects which have the same sheet_name value, and
    therefore expects to find only a single cell_ref value each time, meaning that the list
    produced by groupby() can be removed and the single value return. Returns an exception
    if this list has more than one object.

    Args:
        lst_of_tcs: List of TemplateCell objects.

    Raises:
        RuntimeError: if more than one cell_ref value is found in the list.

    Returns:
        Dictionary whose key is the cell_ref and value is the TemplateCell that contains it.

    """

    output: Dict[str, TemplateCell] = {}
    data = sorted(lst_of_tcs, key=lambda x: x.cell_ref)
    for k, g in groupby(data, key=lambda x: x.cell_ref):
        result = list(g)
        if len(result) > 1:
            raise RuntimeError(
                f"Found duplicate sheet/cell_ref item when extracting keys.")
        else:
            result = result[0]
            output.update({k: result})
    return output


def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> Dict[Any, Any]:
    data: Dict[Any, Any] = {}
    with futures.ProcessPoolExecutor() as pool:
        for file in pool.map(template_reader, xlsx_files):
            data.update(file)
    return data


def hash_single_file(filepath: Path) -> bytes:
    if not filepath.is_file():
        raise RuntimeError(f"Cannot checksum {filepath}")
    else:
        hash_obj = hashlib.md5(open(filepath, "rb").read())
        return hash_obj.digest()


def hash_target_files(list_of_files: List[Path]) -> Dict[str, bytes]:
    """Hash each file in list_of_files.

    Given a list of files, return a dict containing the file name as
    keys and md5 hash as value for each file.
    """
    output = {}
    for file_name in list_of_files:
        if os.path.isfile(file_name):
            hash_obj = hashlib.md5(open(file_name, "rb").read())
            output.update({file_name.name: hash_obj.digest()})
    return output

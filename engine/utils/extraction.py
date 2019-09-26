import fnmatch
import hashlib
import json
import os
from itertools import groupby
from pathlib import Path
from typing import Dict, List, Union
from typing import NamedTuple

from openpyxl.worksheet.cell_range import MultiCellRange
from openpyxl.worksheet.worksheet import Worksheet

from engine.domain.template import TemplateCell

FILE_DATA = Dict[str, Union[str, Dict[str, Dict[str, str]]]]
DAT_DATA = Dict[str, FILE_DATA]
SHEET_DATA_IN_LST = List[Dict[str, str]]
ALL_IMPORT_DATA = Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]]


class ValidationReportItem(NamedTuple):
    """Can be used to allow better access to data from a Data Validation."""
    formula: str
    cell_range: MultiCellRange
    report_line: str


def data_validation_report(sheet: Worksheet) -> List[ValidationReportItem]:
    """Given an openpyxl sheet, produces a list of statements regarding dv cells.
    To be used by the adapters.
    :type sheet: Worksheet
    """
    output = []
    validations = sheet.data_validations.dataValidation
    for v in validations:
        output.append(ValidationReportItem(
            v.formula1,
            v.ranges,
            f"Sheet: {sheet.title}; {v.sqref}; Type: {v.type}; Formula: {v.formula1}",
        ))
    return output


def _check_file_in_datafile(spreadsheet_file: Path, data_file: Path) -> bool:
    """Given a spreadsheet file, checks whether its data is already contained in a data file.
    - Raises KeyError if file not found in data file.
    - Raises FileNotFoundError if either the spreadsheet_file or data_file files cannot be found.
    :type spreadsheet_file: Path
    :type data_file: Path
    """
    # expect the params to be Paths, so we convert
    spreadsheet_file = Path(spreadsheet_file)
    data_file = Path(data_file)
    if not spreadsheet_file.is_file():
        raise FileNotFoundError("Cannot find {}".format(str(spreadsheet_file)))
    if not data_file.is_file():
        raise FileNotFoundError("Cannot find {}".format(str(data_file)))
    f_checksum = _hash_single_file(spreadsheet_file)
    with open(data_file, encoding="utf-8") as f:
        data: DAT_DATA = json.load(f)
        try:
            f_data: FILE_DATA = data[spreadsheet_file.name]
            return f_data["checksum"] == f_checksum
        except KeyError:
            raise KeyError(
                "Data from {} is not contained in {}".format(
                    spreadsheet_file.name, data_file.name
                )
            )


def _get_xlsx_files(directory: str) -> List[Path]:
    """Return a list of Path objects for each xlsx file in directory, or raise an exception."""
    output = []
    if not os.path.isabs(directory):
        raise RuntimeError("Require absolute path here")
    for file_path in os.listdir(directory):
        if fnmatch.fnmatch(file_path, "*.xls[xm]"):
            output.append(Path(os.path.join(directory, file_path)))
    return output


def _get_cell_data(filepath: Path, data, sheet_name: str, cellref: str):
    """Given a Path and a dict of data - and a sheet name, AND a cellref..

    Return:
        - a dict representing the TemplateCell in string format
    """
    _file_data = data[filepath.name]["data"]
    return _file_data[sheet_name][cellref]


def _clean(target_str: str, is_cellref: bool = False) -> str:
    """Rids a string of its most common problems: spacing, capitalisation,etc."""
    if not isinstance(target_str, str):
        raise TypeError("Can only clean a string.")
    output_str = target_str.lstrip().rstrip()
    if is_cellref:
        output_str = output_str.upper()
    return output_str


def _extract_sheets(lst_of_tcs: List[TemplateCell]) -> Dict[str, List[TemplateCell]]:
    """Given a list of TemplateCell objects, returns the list but as a dict sorted by its sheet_name"""
    output: Dict[str, List[TemplateCell]] = {}
    data = sorted(lst_of_tcs, key=lambda x: x.sheet_name)
    for k, group in groupby(data, key=lambda x: x.sheet_name):
        output.update({k: list(group)})
    return output


def _extract_cellrefs(lst_of_tcs: SHEET_DATA_IN_LST):
    """Extract value from TemplateCell.cellref for each TemplateCell in a list to group them.

    When given a list of TemplateCell objects, this function extracts each TemplateCell
    by it's cellref value and groups them according. In the current implementation, this is
    only called on a list of TemplateCell objects which have the same sheet_name value, and
    therefore expects to find only a single cellref value each time, meaning that the list
    produced by groupby() can be removed and the single value return. Returns an exception
    if this list has more than one object.

    Args:
        lst_of_tcs: List of TemplateCell objects.

    Raises:
        RuntimeError: if more than one cellref value is found in the list.

    Returns:
        Dictionary whose key is the cellref and value is the TemplateCell that contains it.

    """
    output = {}
    data = sorted(lst_of_tcs, key=lambda x: x["cellref"])
    for k, group in groupby(data, key=lambda x: x["cellref"]):
        result_lst = list(group)
        if len(result_lst) > 1:
            raise RuntimeError(
                f"Found duplicate sheet/cellref item when extracting keys."
            )
        result_item = result_lst[0]
        output.update({k: result_item})
    return output


def _hash_single_file(filepath: Path) -> str:
    """Return a checksum for a given file at Path.

    Returns checksum string.

    Raises FileNotFoundError if cannot find filepath.
    """
    # if we're given a str, we convert
    filepath = Path(filepath)
    try:
        filepath.is_file()
    except FileNotFoundError:
        raise FileNotFoundError(
            "Cannot find {} in order to calculate checksum".format(filepath)
        )
    hash_obj = hashlib.md5(open(filepath, "rb").read())
    return hash_obj.digest().hex()


def _hash_target_files(list_of_files: List[Path]) -> Dict[str, str]:
    """Hash each file in list_of_files.

    Given a list of files, return a dict containing the file name as
    keys and md5 hash as value for each file.
    """
    output = {}
    for file_name in list_of_files:
        if os.path.isfile(file_name):
            hash_obj = hashlib.md5(open(file_name, "rb").read())
            output.update({file_name.name: hash_obj.digest().hex()})
    return output

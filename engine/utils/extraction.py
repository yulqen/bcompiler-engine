import csv
import datetime
import enum
import fnmatch
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Union

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.cell_range import MultiCellRange
from openpyxl.worksheet.worksheet import Worksheet

from engine.domain.datamap import (DatamapFile, DatamapLine,
                                   DatamapLineValueType)
from engine.domain.template import TemplateCell
from engine.exceptions import MalFormedCSVHeaderException
from engine.utils import ECHO_FUNC_GREEN, ECHO_FUNC_YELLOW

FILE_DATA = Dict[str, Union[str, Dict[str, Dict[str, str]]]]
DAT_DATA = Dict[str, FILE_DATA]
SHEET_DATA_IN_LST = List[Dict[str, str]]
ALL_IMPORT_DATA = Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]]


def datamap_reader(dm_file: Union[Path, str]) -> List[DatamapLine]:
    "Given a datamap csv file, returns a list of DatamapLine objects."
    headers = datamap_check(dm_file)
    data = []
    with DatamapFile(dm_file) as datamap_file:
        reader = csv.DictReader(datamap_file)
        for line in reader:
            if headers["type"] is None:
                data.append(
                    DatamapLine(
                        key=_clean(line[headers["key"]]),
                        sheet=_clean(line[headers["sheet"]]),
                        cellref=_clean(line[headers["cellref"]], is_cellref=True),
                        data_type=None,
                        filename=str(dm_file),
                    )
                )
            else:
                data.append(
                    DatamapLine(
                        key=_clean(line[headers["key"]]),
                        sheet=_clean(line[headers["sheet"]]),
                        cellref=_clean(line[headers["cellref"]], is_cellref=True),
                        data_type=_clean(line[headers["type"]]),
                        filename=str(dm_file),
                    )
                )
    return data


class CheckType(enum.Enum):
    FAIL = enum.auto()
    PASS = enum.auto()
    MISSING_SHEET_REQUIRED_BY_DATAMAP = enum.auto()
    UNDEFINED = enum.auto()


@dataclass
class Check:
    proceed: bool = False
    state: CheckType = CheckType.UNDEFINED
    error_type: CheckType = CheckType.UNDEFINED
    msg: str = ""


def check_datamap_sheets(datamap: Path, template: Union[Path, Workbook, str]) -> Check:
    """Check for valid sheets in a template.

    Check that a template has the sheets expected by the datamap before it has
    its data extracted!
    """
    try:
        worksheets_in_template = template.worksheets  # type: ignore
    except AttributeError:
        wb = load_workbook(template)
        worksheets_in_template = set([sheet.title for sheet in wb.worksheets])
    datamap_data = datamap_reader(datamap)
    worksheets_in_datamap = set([dml.sheet for dml in datamap_data])
    # We only want sheets in the datamap; extraneous sheets should be flagged
    in_template_not_in_datamap = worksheets_in_datamap - worksheets_in_template
    if in_template_not_in_datamap:
        sheets_str = " ".join(list(in_template_not_in_datamap))
        check = Check(
            state=CheckType.FAIL,
            error_type=CheckType.MISSING_SHEET_REQUIRED_BY_DATAMAP,
            msg=f"File {template} has no sheet[s] {sheets_str}",
            proceed=False
        )
    else:
        check = Check(
            state=CheckType.PASS,
            msg="Checked OK.",
            proceed=True
        )
    return check


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
        output.append(
            ValidationReportItem(
                v.formula1,
                v.ranges,
                f"Sheet: {sheet.title}; {v.sqref}; Type: {v.type}; Formula: {v.formula1}",
            )
        )
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


def _get_xlsx_files(directory: Path) -> List[Path]:
    """Return a list of Path objects for each xlsx file in directory, or raise an exception."""
    output = []
    if not os.path.isabs(directory):
        raise RuntimeError("Require absolute path here")
    for file_path in os.listdir(directory):
        if (
            fnmatch.fnmatch(file_path, "*.xls[xm]")
            and "blank_template" not in file_path
        ):
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


def datamap_check(dm_file):
    """Given a datamap csv file, returns a dict of the headers used in reality...

    raises IndexError if less than three headers are found (type header can be None)
    """
    if ECHO_FUNC_YELLOW is not None:
        ECHO_FUNC_YELLOW("Checking datamap file {}\n".format(dm_file))
    _good_keys = ["cell_key", "cellkey", "key"]
    _good_sheet = ["template_sheet", "sheet", "templatesheet"]
    _good_cellref = ["cell_reference", "cell_ref", "cellref", "cellreference"]
    _good_type = ["type", "value_type", "cell_type", "celltype"]
    headers = {}
    using_type = True
    with DatamapFile(dm_file) as datamap_file:
        # initial check - have we got enough headers? If not - raise exception
        top_row = next(datamap_file).rstrip().split(",")
        if len(top_row) == 1:
            raise MalFormedCSVHeaderException(
                "Datamap contains only one header - need at least three to proceed. Quitting."
            )
        if len(top_row) == 2:
            raise MalFormedCSVHeaderException(
                "Datamap contains only two headers - need at least three to proceed. Quitting."
            )
        if top_row[-1] not in _good_type:
            # test if we are using type column here
            headers.update(type=None)
            using_type = False
        if top_row[0] in _good_keys:
            headers.update(key=top_row[0])
        if top_row[1] in _good_sheet:
            headers.update(sheet=top_row[1])
        if top_row[2] in _good_cellref:
            headers.update(cellref=top_row[2])
        if using_type:
            if top_row[3] in _good_type:
                headers.update(type=top_row[3])
    if len(headers.keys()) >= 2:
        # final test - we don't want to proceed unless we have minimum headers
        if not all(
            [x in list(headers.keys()) for x in ["key", "sheet", "cellref", "type"]]
        ):
            raise MalFormedCSVHeaderException(
                "Cannot proceed without required number of headers"
            )
        if ECHO_FUNC_GREEN is not None:
            ECHO_FUNC_GREEN("{} checked ok\n".format(dm_file))
        return headers
    else:
        return MalFormedCSVHeaderException(
            "Datamap does not contain the required headers. Cannot proceed"
        )


def template_reader(template_file) -> Dict[str, Dict[str, Dict[Any, Any]]]:
    "Given a populated xlsx file, returns all data in a list of TemplateCell objects."
    print(("Importing {}".format(template_file)))
    inner_dict: Dict[str, Dict[Any, Any]] = {"data": {}}
    f_path: Path = Path(template_file)
    try:
        workbook = load_workbook(template_file, data_only=True)
    except TypeError:
        msg = (
            "Unable to open {}. Potential corruption of file. Try resaving "
            "in Excel or removing conditionally formatting. See issue at "
            "https://github.com/hammerheadlemon/bcompiler-engine/issues/3 for update. Quitting.".format(
                f_path
            )
        )
        sys.stderr.write(msg + "\n")
        raise
    checksum: str = _hash_single_file(f_path)
    holding = []
    for sheet in workbook.worksheets:
        sheet_data: SHEET_DATA_IN_LST = []
        sheet_dict: Dict[str, Dict[str, Dict[str, str]]] = {}
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
                        elif isinstance(cell.value, (datetime.date, datetime.datetime)):
                            val = cell.value.isoformat()
                            c_type = DatamapLineValueType.DATE
                    cellref = "{}{}".format(cell.column_letter, cell.row)
                    if isinstance(template_file, Path):
                        t_cell = TemplateCell(
                            template_file.as_posix(), sheet.title, cellref, val, c_type
                        ).to_dict()
                    else:
                        t_cell = TemplateCell(
                            template_file, sheet.title, cellref, val, c_type
                        ).to_dict()
                    sheet_data.append(t_cell)
        sheet_dict.update({sheet.title: _extract_cellrefs(sheet_data)})
        holding.append(sheet_dict)
    for sd in holding:
        inner_dict["data"].update(sd)
        inner_dict.update({"checksum": checksum})  # type: ignore
    shell_dict = {f_path.name: inner_dict}
    return shell_dict

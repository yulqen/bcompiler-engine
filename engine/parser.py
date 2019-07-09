import csv
import datetime
import fnmatch
import hashlib
import os
from concurrent import futures
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from itertools import groupby

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


def get_cell_data(
    data: List[TemplateCell], sheet_name: str, cell_ref: str
) -> Optional[TemplateCell]:
    """
    Given a list of TemplateCell items, a sheet name and a cell reference,
    return a single TemplateCell object.
    """
    data_from_cell = [
        cell
        for cell in data
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
                )
            )
    return data


def template_reader(template_file: str) -> Dict:
    """
    Given a populated xlsx file, returns all data in a list of
    TemplateCell objects.
    """
    inner_dict = {}
    data = []
    f_path = Path(template_file)
    print(f"EXTRACTING FROM: {template_file}")
    workbook = load_workbook(template_file, data_only=True)
    checksum = hash_single_file(f_path)
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
                        elif isinstance(cell.value, (datetime.date, datetime.datetime)):
                            val = cell.value
                            c_type = DatamapLineValueType.DATE
                    cell_ref = f"{cell.column_letter}{cell.row}"
                    tc = TemplateCell(template_file, sheet.title, cell_ref, val, c_type)
                    data.append(tc)
    inner_dict.update({"checksum": checksum})
    inner_dict.update({"data": data})
    return inner_dict


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


def _extract_keys(lst_of_tcs: List[TemplateCell]) -> Dict[str, List[TemplateCell]]:
    output: Dict[str, List[TemplateCell]] = {}
    data = sorted(lst_of_tcs, key=lambda x: x.cell_ref)
    for k, g in groupby(data, key=lambda x: x.cell_ref):
        output.update({k: g})
    return output


def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> Dict[Any, Any]:
    data: Dict[Any, Any] = {}
    with futures.ProcessPoolExecutor() as pool:
        for file in pool.map(template_reader, xlsx_files):
            f_name = file["data"][0].file_name.name
            data.update({f_name: file})
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


def order_dataset_by_filename(
    file_list: List[Path], dataset: List[List[TemplateCell]]
) -> Dict:
    """
    Given a list of files and a dataset (a list of list of TemplateCell
    objects - will return a dict of the form:

        dataset = {
        "test_template.xlsx": {
        "checksum": "fjfj34jk22l134hl",
        "data": [TemplateCell(file_name=PosixPath(..),
                 TemplateCell(file_name=PosixPath(..),
                 TemplateCell(file_name=PosixPath(..)
                 ]
                 }
        "test_template2.xlsx": {
        "checksum": "fjfj34jk22l134hl",
        "data": [TemplateCell(file_name=PosixPath(..),
                 TemplateCell(file_name=PosixPath(..),
                 TemplateCell(file_name=PosixPath(..)
                 ]
                 }
        }

    """
    file_hashes = hash_target_files(file_list)
    _main_dict = {}
    for lst in dataset:
        fn = lst[0].file_name.name
        _data_dict = {"file_checksum": file_hashes[fn]}
        _data_dict.update(data=lst)
        _main_dict.update({fn: _data_dict})
    return _main_dict

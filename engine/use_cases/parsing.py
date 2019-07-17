"""
Mostly, this module is about organising the main data structure.

Given a list of files and a dataset (a list of list of TemplateCell
objects - will return a dict of the form:

    dataset = {
    "test_template.xlsx": {
    "checksum": "fjfj34jk22l134hl",
    "data": {
        "Summary": {
            "A1": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A2": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A2": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
        },
        "Finances": {
            "A1": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A4": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A10": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
        }
    "test_template2.xlsx": {
    "checksum": "AFfjdddfa4jk134hl",
    "data": {
        "Summary": {
            "A1": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A2": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A2": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
        },
        "Finances": {
            "A1": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A4": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
            "A10": {"file_name": "test_file.xslx", "sheet": "Sheet 1"...,
        }
    }
"""
import csv
import datetime
from concurrent import futures
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from openpyxl import load_workbook

from ..domain.datamap import DatamapLine, DatamapLineValueType
from ..domain.template import TemplateCell
from ..utils.extraction import _clean, _extract_cellrefs, _hash_single_file

if TYPE_CHECKING:
    from ..repository.templates import Repo


class ParsePopulatedTemplatesUseCase:
    def __init__(self, repo: "Repo"):
        self.repo = repo

    def execute(self) -> str:
        return self.repo.list_as_json()


class ParseDatamapUseCase:
    def __init__(self, repo: "Repo"):
        self.repo = repo

    def execute(self) -> str:
        return self.repo.list_as_json()


class DatamapFile:
    """A context manager that represents the datamap file.

    Having a context manager means we can more elegantly capture the
    exception with the file isn't found.
    """

    def __init__(self, filepath):
        "Creates the context manager"
        self.filepath = filepath

    def __enter__(self):
        try:
            self.f_obj = open(self.filepath, "r", encoding="utf-8")
            return self.f_obj
        except FileNotFoundError:
            raise

    def __exit__(self, type, value, traceback):
        self.f_obj.close()


def datamap_reader(dm_file: Path) -> List[DatamapLine]:
    """
    Given a datamap csv file, returns a list of DatamapLine objects.
    """
    data = []
    with DatamapFile(dm_file) as datamap_file:
        reader = csv.DictReader(datamap_file)
        for line in reader:
            data.append(
                DatamapLine(
                    key=_clean(line["cell_key"]),
                    sheet=_clean(line["template_sheet"]),
                    cellref=_clean(line["cellreference"], is_cellref=True),
                    data_type=_clean(line["type"]),
                    filename=dm_file,
                ))
    return data


def template_reader(template_file: Path
                    ) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Given a populated xlsx file, returns all data in a list of
    TemplateCell objects.
    """
    inner_dict: dict = {"data": {}}
    f_path = Path(template_file)
    print(f"EXTRACTING FROM: {template_file}")
    workbook = load_workbook(template_file, data_only=True)
    checksum = _hash_single_file(f_path)
    holding = []
    for sheet in workbook.worksheets:
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
                            val = cell.value.isoformat()
                            c_type = DatamapLineValueType.DATE
                    cellref = f"{cell.column_letter}{cell.row}"
                    if isinstance(template_file, Path):
                        tc = TemplateCell(template_file.as_posix(),
                                          sheet.title, cellref, val,
                                          c_type).to_dict()
                    else:
                        tc = TemplateCell(template_file, sheet.title, cellref,
                                          val, c_type).to_dict()
                    sheet_data.append(tc)
        sheet_dict.update({sheet.title: _extract_cellrefs(sheet_data)})
        holding.append(sheet_dict)
    for sd in holding:
        inner_dict["data"].update(sd)
    inner_dict.update({"checksum": checksum})
    shell_dict = {f_path.name: inner_dict}
    return shell_dict


# here is the version with out multiprocessing
# def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> set:
#    data = []
#    for file in map(template_reader, xlsx_files):
#        data.append(file)
#    return data


def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> Dict[Any, Any]:
    data: Dict[Any, Any] = {}
    with futures.ProcessPoolExecutor() as pool:
        for file in pool.map(template_reader, xlsx_files):
            data.update(file)
    return data

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
import json
import logging
from concurrent import futures
from pathlib import Path
from typing import IO, List

from openpyxl import load_workbook

from engine.domain.datamap import DatamapLine, DatamapLineValueType
from engine.domain.template import TemplateCell
from engine.utils.extraction import (_clean, _extract_cellrefs,
                                     _hash_single_file)

# pylint: disable=R0903,R0913;


logger = logging.getLogger(__name__)
logger.setLevel("INFO")


class ParsePopulatedTemplatesUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self):
        return self.repo.list_as_json()


class ApplyDatamapToExtractionUseCase:
    "Extract data from a bunch of spreadsheets, but filter based on a datamap."

    def __init__(self, datamap_repo, template_repo) -> None:
        self.datamap_repo = datamap_repo
        self.template_repo = template_repo

    def _comb_with_datamap(self, filename, template_data, datamap_data, key, sheet):
        """Given a filename, a template_data json str, a datamap_data dict, key and sheet, returns
        the value in the spreadsheet at given datamap key.
        """
        _data_lst = json.loads(datamap_data)
        if key not in [x["key"] for x in _data_lst]:
            raise KeyError("No key \"{}\" in datamap".format(key))
        if sheet not in [x["sheet"] for x in _data_lst]:
            raise KeyError("No sheet \"{}\" in datamap".format(sheet))
        _target_cellref = [x["cellref"] for x in _data_lst if x["key"] == key and x["sheet"] == sheet]
        _cellref = _target_cellref[0]
        return json.loads(template_data)[filename]["data"][sheet][_cellref]["value"]


    def query_key(self, filename, key, sheet):
        """Given a filename, key and sheet, raises the value in the spreadsheet.

        Raises KeyError if any of filename, key and sheet are not in the datamap.
        """
        t_uc = ParsePopulatedTemplatesUseCase(self.template_repo)
        d_uc = ParseDatamapUseCase(self.datamap_repo)
        template_data = t_uc.execute()
        datamap_data = d_uc.execute()
        try:
            return self._comb_with_datamap(filename, template_data, datamap_data, key, sheet)
        except KeyError:
            raise




class ParseDatamapUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self):
        return self.repo.list_as_json()


class DatamapFile:
    """A context manager that represents the datamap file.

    Having a context manager means we can more elegantly capture the
    exception with the file isn't found.
    """

    def __init__(self, filepath: str) -> None:
        "Create the context manager"
        self.filepath = filepath

    def __enter__(self) -> IO[str]:
        try:
            self.f_obj = open(self.filepath, "r", encoding="utf-8")
            return self.f_obj
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find {}".format(self.filepath))

    def __exit__(self, mytype, value, traceback):  # type: ignore
        self.f_obj.close()


def datamap_reader(dm_file: str) -> List[DatamapLine]:
    "Given a datamap csv file, returns a list of DatamapLine objects."
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
                )
            )
    return data


def template_reader(template_file):
    "Given a populated xlsx file, returns all data in a list of TemplateCell objects."
    inner_dict = {"data": {}}
    f_path = Path(template_file)
    logger.info("Extracting from: {}".format(f_path.name))
    workbook = load_workbook(template_file, data_only=True)
    checksum = _hash_single_file(f_path)
    holding = []
    for sheet in workbook.worksheets:
        logger.info("Processing sheet {} | {}".format(f_path.name, sheet.title))
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
    inner_dict.update({"checksum": checksum})
    shell_dict = {f_path.name: inner_dict}
    return shell_dict


# here is the version with out multiprocessing
# def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> set:
#    data = []
#    for file in map(template_reader, xlsx_files):
#        data.append(file)
#    return data


def extract_from_multiple_xlsx_files(xlsx_files):
    "Extract raw data from list of paths to excel files. Return as complex dictionary."
    data = {}
    with futures.ProcessPoolExecutor() as pool:
        for file in pool.map(template_reader, xlsx_files):
            data.update(file)
    return data

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
import sys
import warnings
from concurrent import futures
from pathlib import Path
from typing import IO, Any, Dict, List

from openpyxl import load_workbook

from engine.domain.datamap import DatamapLine, DatamapLineValueType
from engine.domain.template import TemplateCell
from engine.utils.extraction import (ALL_IMPORT_DATA, SHEET_DATA_IN_LST,
                                     _clean, _extract_cellrefs,
                                     _hash_single_file)

# pylint: disable=R0903,R0913;

warnings.filterwarnings("ignore", ".*Data Validation*.")

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


# function monkeypatched from adapter code into here which can wrap statements intended for output
ECHO_FUNC_RED = None
ECHO_FUNC_GREEN = None
ECHO_FUNC_YELLOW = None
ECHO_FUNC_WHITE = None


class MalFormedCSVHeaderException(Exception):
    pass


class ParsePopulatedTemplatesUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self) -> str:
        return self.repo.list_as_json()  # type: ignore


class ApplyDatamapToExtractionUseCase:
    "Extract data from a bunch of spreadsheets, but filter based on a datamap."

    def __init__(self, datamap_repo, template_repo) -> None:
        self._datamap_repo = datamap_repo
        self._template_repo = template_repo
        self._template_data_dict: ALL_IMPORT_DATA = {}
        self._datamap_data_dict: List[Dict[str, str]] = []
        self.data_for_master: List[ALL_IMPORT_DATA] = []
        self._datamap_data_json: str = ""
        self._template_data_json: str = ""

    def _get_value_of_cell_referred_by_key(
        self, filename: str, key: str, sheet: str
    ) -> str:
        """Given a filename, a template_data json str, a datamap_data dict, key and sheet, returns
        the value in the spreadsheet at given datamap key.

        Throws KeyError if the datamap refers to a sheet/cellref combo in the target file that does not exist.
        """
        output = ""
        if key not in [x["key"] for x in self._datamap_data_dict]:
            raise KeyError('No key "{}" in datamap'.format(key))
        if sheet not in [x["sheet"] for x in self._datamap_data_dict]:
            raise KeyError('No sheet "{}" in datamap'.format(sheet))
        _target_cellref = [
            x["cellref"]
            for x in self._datamap_data_dict
            if x["key"] == key and x["sheet"] == sheet
        ]
        _cellref = _target_cellref[0]
        try:
            output = self._template_data_dict[filename]["data"][sheet][_cellref][
                "value"
            ]
        except KeyError as e:
            if e.args[0] == sheet:
                logger.critical(
                    "No sheet named {} in {}. Unable to process.".format(
                        sheet, filename
                    )
                )
                raise KeyError(
                    "No sheet named {} in {}. Unable to process.".format(
                        sheet, filename
                    )
                )
        return output

    def _set_datamap_and_template_data(self) -> None:
        "Does the work of creating the template_data and datamap_data attributes"
        t_uc = ParsePopulatedTemplatesUseCase(self._template_repo)
        d_uc = ParseDatamapUseCase(self._datamap_repo)
        self._datamap_data_json = d_uc.execute()
        self._template_data_json = t_uc.execute()

    def get_values(self):
        for _file_name in self._template_data_dict:
            for _dml in self._datamap_data_dict:
                val = self.query_key(_file_name, _dml["key"], _dml["sheet"])
                yield {(_file_name, _dml["key"], _dml["sheet"], _dml["cellref"]): val}

    def execute(self, as_obj=False, for_master=False):
        if self._template_data_dict is not True and self._datamap_data_dict is not True:
            self._set_datamap_and_template_data()
        self._datamap_data_dict = json.loads(self._datamap_data_json)
        self._template_data_dict = json.loads(self._template_data_json)
        if for_master:
            self._format_data_for_master()

    def query_key(self, filename, key, sheet):
        """Given a filename, key and sheet, raises the value in the spreadsheet.

        Raises KeyError if any of filename, key and sheet are not in the datamap.
        """
        if not bool(self._template_data_dict) and bool(self._datamap_data_dict):
            self._set_datamap_and_template_data()
        try:
            return self._get_value_of_cell_referred_by_key(filename, key, sheet)
        except KeyError:
            logger.critical(
                "Unable to process datamapline due to problem with sheet/cellref referred to by datamap"
            )
            raise

    def _format_data_for_master(self):
        output = [{fname: []} for fname in self._template_data_dict]
        # FIXME - this is where crash is happening
        # see test test_master_from_org_templates/test_create_master_spreadsheet
        f_data = self._template_data_dict
        dm_data = self._datamap_data_dict
        for _file_name in f_data:
            for _dml in dm_data:
                val = self.query_key(_file_name, _dml["key"], _dml["sheet"])
                _col_dict = [d for d in output if list(d.keys())[0] == _file_name][0]
                _col_dict[_file_name].append((_dml["key"], val))
        self.data_for_master = output


class CreateMasterUseCase:
    def __init__(self, datamap_repo, template_repo, output_repository):
        self.datamap_repo = datamap_repo
        self.template_repo = template_repo
        self.output_repository = output_repository

    def execute(self, output_file_name):
        uc = ApplyDatamapToExtractionUseCase(self.datamap_repo, self.template_repo)
        uc.execute(for_master=True)
        output_repo = self.output_repository(uc.data_for_master, output_file_name)
        output_repo.save()


class ParseDatamapUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, obj=False):
        if not obj:
            return self.repo.list_as_json()  # type: ignore
        else:
            return self.repo.list_as_objs()


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
            self.f_obj.read()
            self.f_obj.seek(0)
            return self.f_obj
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find {}".format(self.filepath))
        except UnicodeDecodeError:
            self.f_obj = open(self.filepath, "r", encoding="latin1")
            return self.f_obj

    def __exit__(self, mytype, value, traceback):  # type: ignore
        self.f_obj.close()


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
            logger.info("Using {} as header".format(top_row[0]))
        if top_row[1] in _good_sheet:
            headers.update(sheet=top_row[1])
            logger.info("Using {} as header".format(top_row[1]))
        if top_row[2] in _good_cellref:
            headers.update(cellref=top_row[2])
            logger.info("Using {} as header".format(top_row[2]))
        if using_type:
            if top_row[3] in _good_type:
                headers.update(type=top_row[3])
                logger.info("Using {} as header".format(top_row[3]))
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


def datamap_reader(dm_file: str) -> List[DatamapLine]:
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
                        filename=dm_file,
                    )
                )
            else:
                data.append(
                    DatamapLine(
                        key=_clean(line[headers["key"]]),
                        sheet=_clean(line[headers["sheet"]]),
                        cellref=_clean(line[headers["cellref"]], is_cellref=True),
                        data_type=_clean(line[headers["type"]]),
                        filename=dm_file,
                    )
                )
    return data


def template_reader(template_file) -> Dict[str, Dict[str, Dict[Any, Any]]]:
    "Given a populated xlsx file, returns all data in a list of TemplateCell objects."
    print(("Importing {}".format(template_file)))
    inner_dict: Dict[str, Dict[Any, Any]] = {"data": {}}
    f_path: Path = Path(template_file)
    logger.info("Extracting from: {}".format(f_path.name))
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
        logger.critical(msg)
        sys.stderr.write(msg + "\n")
        raise
    checksum: str = _hash_single_file(f_path)
    holding = []
    for sheet in workbook.worksheets:
        logger.info("Processing sheet {} | {}".format(f_path.name, sheet.title))
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


# here is the version with out multiprocessing
# def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> set:
#    data = []
#    for file in map(template_reader, xlsx_files):
#        data.append(file)
#    return data


def extract_from_multiple_xlsx_files(xlsx_files) -> ALL_IMPORT_DATA:
    "Extract raw data from list of paths to excel files. Return as complex dictionary."
    data = {}
    with futures.ProcessPoolExecutor() as pool:
        for file in pool.map(template_reader, xlsx_files):
            data.update(file)
    return data

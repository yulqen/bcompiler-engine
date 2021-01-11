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
import json
import logging
import warnings
from concurrent import futures
from typing import Dict, List

from engine.exceptions import (
    DatamapNotCSVException,
    NoApplicableSheetsInTemplateFiles,
    RemoveFileWithNoSheetRequiredByDatamap,
)

# pylint: disable=R0903,R0913;
from engine.utils.extraction import (
    ALL_IMPORT_DATA,
    check_datamap_sheets,
    remove_failing_files,
    template_reader,
)

warnings.filterwarnings("ignore", ".*Data Validation*.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)

# TODO - move this to config
SKIP_MISSING_SHEETS = False


class ParsePopulatedTemplatesUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self) -> str:
        return self.repo.list_as_json()  # type: ignore


class ApplyDatamapToExtractionUseCase:
    """Extract data from a bunch of spreadsheets, but filter based on a datamap."""

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
        """Does the work of creating the template_data and datamap_data attributes"""
        t_uc = ParsePopulatedTemplatesUseCase(self._template_repo)
        d_uc = ParseDatamapUseCase(self._datamap_repo)
        try:
            self._datamap_data_json = d_uc.execute()
        except DatamapNotCSVException:
            raise
        self._template_data_json = t_uc.execute()

    def get_values(self):
        for _file_name in self._template_data_dict:
            for _dml in self._datamap_data_dict:
                val = self.query_key(_file_name, _dml["key"], _dml["sheet"])
                yield {(_file_name, _dml["key"], _dml["sheet"], _dml["cellref"]): val}

    def execute(self, as_obj=False, for_master=False):
        if self._template_data_dict is not True and self._datamap_data_dict is not True:
            try:
                self._set_datamap_and_template_data()
            except DatamapNotCSVException:
                raise
        self._datamap_data_dict = json.loads(self._datamap_data_json)
        self._template_data_dict = json.loads(self._template_data_json)
        # TODO - the complete data as a dict is available as self._template_data_dict
        logger.info("Checking template data.")
        checks = check_datamap_sheets(self._datamap_data_dict, self._template_data_dict)
        # TODO -reintroduce SKIP_MISSING_SHEETS check here
        # We set a config variable to choose whether we
        # throw out files with a single missing sheet
        try:
            self._template_data_dict = remove_failing_files(
                checks, self._template_data_dict
            )
        except NoApplicableSheetsInTemplateFiles:
            # TODO add log message here
            # for now...
            # logger.critical("There are no files containing sheets declared in datamap. Quitting.")
            raise
        except RemoveFileWithNoSheetRequiredByDatamap as e:
            logging.warning(
                f"{e.args[0][0]} does not contain the sheets required by datamap (eg. {e.args[0][1]}). Not set to "
                f"skip sheets so omitting from master. "
            )
            raise
        # TODO - we have to do something when SKIP_MISSING_SHEETS is True here
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
        try:
            uc.execute(for_master=True)
        except DatamapNotCSVException:
            raise
        output_repo = self.output_repository(uc.data_for_master, output_file_name)
        output_repo.save()


class ParseDatamapUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, obj=False):
        if not obj:
            try:
                return self.repo.list_as_json()  # type: ignore
            except DatamapNotCSVException:
                raise
        else:
            return self.repo.list_as_objs()


# here is the version with out multiprocessing
# def parse_multiple_xlsx_files(xlsx_files: List[Path]) -> set:
#    data = []
#    for file in map(template_reader, xlsx_files):
#        data.append(file)
#    return data


def extract_from_multiple_xlsx_files(xlsx_files) -> ALL_IMPORT_DATA:
    """Extract raw data from list of paths to excel files. Return as complex dictionary."""
    data = {}
    with futures.ProcessPoolExecutor() as pool:
        for file in pool.map(template_reader, xlsx_files):
            data.update(file)
    return data

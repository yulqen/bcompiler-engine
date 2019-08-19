import json
import os
from pathlib import Path

from openpyxl import Workbook, load_workbook

from engine.use_cases.parsing import \
    extract_from_multiple_xlsx_files as extract
from engine.utils.extraction import ALL_IMPORT_DATA, _get_xlsx_files

from ..config import Config


class MultipleTemplatesWriteRepo:
    """Write data to a blank template.

    Given data (e.g. from extracted from a master xlsx file), writes
    each data set to a blank template and save it in the output directory,
    which by default is in "User/Documents/bcompiler/output."
    """
    def __init__(self, blank_template: Path):
        "directory_path is the directory in which to write the files."
        self.output_path = Config.PLATFORM_DOCS_DIR / "output"
        self.blank_template = blank_template

    def _populate_workbook(self, workbook: Workbook, file_data) -> None:
        # get sheets from file_data
        sheets = {x.sheet for x in file_data}
        # TODO - raise exception here if not sheets
        for sheet in sheets:
            _sheet = workbook.get_sheet_by_name(sheet)
            for cell in file_data:
                _sheet[cell.cellref].value = cell.value

    def write(self, data, file_name, from_json: bool = False) -> None:
        """Writes data from a single column in a master Excel file to a file.

        data: list of ColData tuples, which contains the key, sheet and value
        file_name: file name to be appended to output path
        """
        for file_data in data:
            workbook = load_workbook(
                self.blank_template, read_only=False, keep_vba=True
            )
            self._populate_workbook(workbook, file_data)
            output_file = ".".join([file_name, "xlsm"])
            workbook.save(filename=Config.PLATFORM_DOCS_DIR / "output" / output_file)


class FSPopulatedTemplatesRepo:
    "A repo that is based on a single data file in the .bcompiler-engine directory."

    def __init__(self, directory_path: str):
        self.directory_path = directory_path

    def list_as_json(self) -> str:
        "Try to open the data file containing populated data as json."
        try:
            with open(
                os.path.join(Config.BCOMPILER_LIBRARY_DATA_DIR, "extracted_data.dat")
            ) as data_file:
                return data_file.read()
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find file.")


class InMemoryPopulatedTemplatesRepository:
    "A repo that does no data file reading or writing - just parsing from excel files."

    def __init__(self, directory_path: str) -> None:
        self.directory_path = directory_path
        self.state: ALL_IMPORT_DATA = {}

    def list_as_json(self) -> str:
        "Return data from a directory of populated templates as json."
        excel_files = _get_xlsx_files(self.directory_path)
        if not self.state:
            self.state = extract(excel_files)
            return json.dumps(self.state)
        else:
            return json.dumps(self.state)

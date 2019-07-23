import json
import shutil

import pytest

from engine.repository.templates import (FSPopulatedTemplatesRepo,
                                         InMemoryPopulatedTemplatesRepository)
from engine.use_cases.parsing import ParsePopulatedTemplatesUseCase
from engine.utils.extraction import check_file_in_datafile


def test_template_parser_use_case(resources):
    repo = InMemoryPopulatedTemplatesRepository(resources)
    parse_populated_templates_use_case = ParsePopulatedTemplatesUseCase(repo)
    result = parse_populated_templates_use_case.execute()
    assert (
        json.loads(result)["test_template.xlsx"]["data"]["Summary"]["B3"]["value"]
        == "This is a string"
    )


def test_query_data_from_data_file(
    mock_config, dat_file, spreadsheet_same_data_as_dat_file
):
    mock_config.initialise()
    shutil.copy2(dat_file, mock_config.BCOMPILER_LIBRARY_DATA_DIR)
    shutil.copy2(spreadsheet_same_data_as_dat_file, mock_config.PLATFORM_DOCS_DIR)
    repo = FSPopulatedTemplatesRepo(mock_config.PLATFORM_DOCS_DIR)
    parse_populated_templates_use_case = ParsePopulatedTemplatesUseCase(repo)
    result = parse_populated_templates_use_case.execute()
    assert (
        json.loads(result)["test_dat_file_use_case.xlsx"]["data"]["new sheet"]["A1"]["value"]
        == "Project/Programme Name"
    )


def test_datamap_applied_to_extracted_data_returns_a_generator():
    """The use case needs to apply the datamap to the data returned from a repo.

    The repository is on the access layer of this library. The UI application
    is required to be aware of this and create the correct repository (currently
    available is an in-memory repository or a file system repository, which should
    be the default.

    - Check whether there is a data file containing the data required
    - If there is, pull that data out of the dat file
    - If it isn't, pull that data out of the excel files
    - Convert the data to a usable object
    - The repo pulls all the data from the directory.

    # TODO - func to check for dat file and whether contained data is target of current extraction
    # TODO - allow for the default repository to be set in the config? (in the application)
    """
    pass


def ensure_data_and_populate_file(config, dat_file, spreadsheet_file) -> None:
    "Ensure the data in a single file is mirrored in a dat file, in correct location for testing"
    shutil.copy2(dat_file, config.BCOMPILER_LIBRARY_DATA_DIR)
    shutil.copy2(spreadsheet_file, config.PLATFORM_DOCS_DIR)



def test_file_data_is_in_dat_file(mock_config, dat_file, spreadsheet_same_data_as_dat_file):
    """Before we do any data extraction from files, we need to check out dat file.
    """
    mock_config.initialise()
    ensure_data_and_populate_file(mock_config, dat_file, spreadsheet_same_data_as_dat_file)
    assert check_file_in_datafile(spreadsheet_same_data_as_dat_file, dat_file)


def test_file_data_not_in_data_returns_exception(mock_config, dat_file, spreadsheet_one_cell_different_data_than_dat_file):
    """Before we do any data extraction from files, we need to check out dat file.

    If file data is not contained in the dat file, we need to know about it by getting a False return.
    """
    mock_config.initialise()
    ensure_data_and_populate_file(mock_config, dat_file, spreadsheet_one_cell_different_data_than_dat_file)
    with pytest.raises(KeyError) as excinfo:
        check_file_in_datafile(spreadsheet_one_cell_different_data_than_dat_file, dat_file)
    exception_msg = excinfo.value.args[0]
    assert exception_msg == "Data from test_data_file_use_case_diff_data_from_dat_file.xlsx is not contained in extracted_data.dat"

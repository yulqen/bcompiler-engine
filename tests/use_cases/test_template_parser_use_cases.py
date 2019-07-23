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
        json.loads(result)["test.xlsx"]["data"]["new sheet"]["A1"]["value"]
        == "Project/Programme Name"
    )


@pytest.mark.skip("Not ready")
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


@pytest.mark.skip("Not ready")
def test_file_data_is_in_dat_file(mock_config, dat_file, spreadsheet_same_data_as_dat_file):
    """Before we do any data extraction from files, we need to check out dat file.
    """

    mock_config.initialise()
    shutil.copy2(dat_file, mock_config.BCOMPILER_LIBRARY_DATA_DIR)
    shutil.copy2(spreadsheet_same_data_as_dat_file, mock_config.PLATFORM_DOCS_DIR)
    assert check_file_in_datafile(spreadsheet_same_data_as_dat_file, dat_file)

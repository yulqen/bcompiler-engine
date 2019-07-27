import json
import shutil
from pathlib import Path

import pytest

from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.repository.templates import (FSPopulatedTemplatesRepo,
                                         InMemoryPopulatedTemplatesRepository)
from engine.use_cases.parsing import (ApplyDatamapToExtractionUseCase,
                                      ParsePopulatedTemplatesUseCase)
from engine.utils.extraction import _check_file_in_datafile


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
        json.loads(result)["test_dat_file_use_case.xlsx"]["data"]["new sheet"]["A1"][
            "value"
        ]
        == "Project/Programme Name"
    )


def test_in_memory_datamap_application_to_extracted_data(
    mock_config, doc_directory, datamap, template
):
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap)
    uc = ApplyDatamapToExtractionUseCase(dm_repo, tmpl_repo)
    assert (
        uc.query_key("test_template.xlsx", "String Key", "Summary")
        == "This is a string"
    )
    assert uc.query_key("test_template.xlsx", "Big Float", "Another Sheet") == 7.2


def test_in_memory_datamap_application_to_extracted_data_raises_exception(
    mock_config, doc_directory, datamap, template
):
    "Raise exception when the key provided is not in the datamap"
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap)
    uc = ApplyDatamapToExtractionUseCase(dm_repo, tmpl_repo)
    with pytest.raises(KeyError):
        # note the extra space in the key name
        uc.query_key("test_template.xlsx", "Funny Date ", "Another Sheet")
    with pytest.raises(KeyError):
        # note the extra space in the sheet name
        uc.query_key("test_template.xlsx", "Funny Date", "Another Sheet ")


def test_in_memory_datamap_application_throws_exception_wrong_sheet(
    mock_config, doc_directory, datamap_match_test_template, bad_sheet_template
):
    with pytest.raises(KeyError):
        mock_config.initialise()
        shutil.copy2(bad_sheet_template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
        tmpl_repo = InMemoryPopulatedTemplatesRepository(
            mock_config.PLATFORM_DOCS_DIR / "input"
        )
        dm_repo = InMemorySingleDatamapRepository(datamap_match_test_template)
        uc = ApplyDatamapToExtractionUseCase(dm_repo, tmpl_repo)
        uc.execute()
        data = uc.get_values()
        next(data)


def test_in_memory_datamap_generator(
    mock_config, doc_directory, datamap_match_test_template, template
):
    "Doesn't really need a generator because its already in memory, but whatever..."
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap_match_test_template)
    uc = ApplyDatamapToExtractionUseCase(dm_repo, tmpl_repo)
    uc.execute()
    data = uc.get_values()
    #   assert next(uc.get_values(as_obj=True)) == {("test_template.xlsx", "Summary", "B2"): datetime.date(2019, 10, 19)}
    assert next(data) == {
        ("test_template.xlsx", "Summary", "B2"): "2019-10-20T00:00:00"
    }
    assert next(data) == {("test_template.xlsx", "Summary", "B3"): "This is a string"}
    assert next(data) == {("test_template.xlsx", "Another Sheet", "F17"): 7.2}


@pytest.mark.skip("This is for FS process - we want to do in mem first")
def test_datamap_applied_to_extracted_data_returns_expected_value(
    mock_config, datamap, resources
):
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


def test_file_data_is_in_dat_file(
    mock_config, dat_file, spreadsheet_same_data_as_dat_file
):
    """Before we do any data extraction from files, we need to check out dat file.
    """
    mock_config.initialise()
    ensure_data_and_populate_file(
        mock_config, dat_file, spreadsheet_same_data_as_dat_file
    )
    assert _check_file_in_datafile(spreadsheet_same_data_as_dat_file, dat_file)


def test_file_data_is_in_dat_file_works_with_str_params(
    mock_config, dat_file, spreadsheet_same_data_as_dat_file
):
    """Before we do any data extraction from files, we need to check out dat file.
    """
    mock_config.initialise()
    ensure_data_and_populate_file(
        mock_config, dat_file, spreadsheet_same_data_as_dat_file
    )
    assert _check_file_in_datafile(
        str(spreadsheet_same_data_as_dat_file), str(dat_file)
    )


def test_if_data_file_and_spreadsheet_file_dont_exist():
    with pytest.raises(FileNotFoundError) as exinfo:
        _check_file_in_datafile("no_spreadsheet_file.xlsx", "no_dat_file.xlsx")
    msg = exinfo.value.args[0]
    assert "Cannot find" in msg


def test_file_data_is_in_data_file__but_spreadsheet_file_doesnt_exist(
    mock_config, dat_file
):
    mock_config.initialise()
    with pytest.raises(FileNotFoundError):
        _check_file_in_datafile("/home/non-existant-file.txt", dat_file)


def test_file_data_not_in_data_returns_exception(
    mock_config, dat_file, spreadsheet_one_cell_different_data_than_dat_file
):
    """Before we do any data extraction from files, we need to check out dat file.

    If file data is not contained in the dat file, we need to know about it by getting a False return.
    """
    mock_config.initialise()
    ensure_data_and_populate_file(
        mock_config, dat_file, spreadsheet_one_cell_different_data_than_dat_file
    )
    with pytest.raises(KeyError) as excinfo:
        _check_file_in_datafile(
            spreadsheet_one_cell_different_data_than_dat_file, dat_file
        )
    exception_msg = excinfo.value.args[0]
    assert (
        exception_msg
        == "Data from test_data_file_use_case_diff_data_from_dat_file.xlsx is not contained in extracted_data.dat"
    )

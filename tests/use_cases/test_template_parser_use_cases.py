import json
import shutil
from pathlib import Path

from engine.config import Config
from engine.repository.templates import (FSPopulatedTemplatesRepo,
                                         InMemoryPopulatedTemplatesRepository)
from engine.use_cases.parsing import (ApplyDatamapToExtraction, DatamapFile,
                                      ParsePopulatedTemplatesUseCase)


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


def test_datamap_applied_to_extracted_data_returns_a_generator(
    mock_config, datamap, pop_template
):
    mock_config.initialise()
    shutil.copy2(
        Path.cwd() / "tests/resources/pop_template_for_datamap_test.xlsm",
        Config.PLATFORM_DOCS_DIR / "input",
    )
    repo = FSPopulatedTemplatesRepo(mock_config.PLATFORM_DOCS_DIR)
    datamap_file = DatamapFile(datamap)
    apply_datamap_uc = ApplyDatamapToExtraction(repo, datamap_file)
    result = apply_datamap_uc.execute()

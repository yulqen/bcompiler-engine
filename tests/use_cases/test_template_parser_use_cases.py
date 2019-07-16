import json
import os
import shutil
from pathlib import Path

from engine.repository.templates import (FSPopulatedTemplatesRepo,
                                         InMemoryPopulatedTemplatesRepository)
from engine.use_cases.parsing import ParsePopulatedTemplatesUseCase


def test_template_parser_use_case(resources):
    repo = InMemoryPopulatedTemplatesRepository(resources)
    parse_populated_templates_use_case = ParsePopulatedTemplatesUseCase(repo)
    result = parse_populated_templates_use_case.execute()
    assert (json.loads(result)["test_template.xlsx"]["data"]["Summary"]["B3"]
            ["value"] == "This is a string")


def test_can_get_config_value(mock_config):
    mock_config.initialise()
    config = mock_config.config_parser
    assert (config["PATHS"]["import directory"] ==
            "/home/lemon/Documents/bcompiler/import")


def test_query_data_from_data_file(mock_config, dat_file):
    mock_config.initialise()
    shutil.copy2(dat_file, mock_config.BCOMPILER_LIBRARY_DATA_DIR)
    repo = FSPopulatedTemplatesRepo(Path.home() / "Desktop")
    parse_populated_templates_use_case = ParsePopulatedTemplatesUseCase(repo)
    result = parse_populated_templates_use_case.execute()
    assert (json.loads(result)["test.xlsx"]["data"]["new sheet"]["A1"]["value"]
            == "Project/Programme Name")

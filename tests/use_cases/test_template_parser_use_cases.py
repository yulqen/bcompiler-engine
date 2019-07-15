import json
import os
import shutil
from pathlib import Path

import pytest

from engine.repository.templates import (FSPopulatedTemplatesRepo,
                                         InMemoryPopulatedTemplatesRepository)
from engine.serializers.template import ParsedTemplatesSerializer
from engine.use_cases.parsing import ParsePopulatedTemplatesUseCase


def test_template_parser_use_case(resources):
    repo = InMemoryPopulatedTemplatesRepository(resources)
    parse_populated_templates_use_case = ParsePopulatedTemplatesUseCase(repo)
    result = parse_populated_templates_use_case.execute()
    assert (json.loads(result)["test_template.xlsx"]["data"]["Summary"]["B3"]
            ["value"] == "This is a string")


def test_query_data_from_data_file(mock_config, dat_file):
    # TODO - currently fails as we need to pass config.data_dir (not a thing,
    # but you know what I mean) needs to get to list_as_json() on the repo class.
    # I need to find a better way of doing config - best to use configparser and ini
    # files (https://hackersandslackers.com/simplify-your-python-projects-configuration/)
    # TODO - amend mock_config in conftest.py to accommodate the above
    mock_config.initialise()
    shutil.copy2(dat_file, mock_config.BCOMPILER_LIBRARY_DATA_DIR)
    repo = FSPopulatedTemplatesRepo(Path.home() / "Desktop")
    parse_populated_templates_use_case = ParsePopulatedTemplatesUseCase(repo)
    result = parse_populated_templates_use_case.execute()

# type: ignore

import json
import os
from typing import List

import pytest
from engine.exceptions import DatamapNotCSVException
from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.utils.extraction import extract_zip_file_to_tmpdir
from openpyxl import load_workbook


def test_datamapline_repository_single_file_repo(datamap, datamapline_list_objects):
    repo = InMemorySingleDatamapRepository(datamap)
    assert repo.list_as_objs()[0].key == datamapline_list_objects[0].key
    assert repo.list_as_objs()[0].sheet == datamapline_list_objects[0].sheet
    assert json.loads(repo.list_as_json())[0]["key"] == "Project/Programme Name"


def test_datamapline_repository_non_existant_file(datamapline_list_objects):
    with pytest.raises(DatamapNotCSVException):
        repo = InMemorySingleDatamapRepository("non-file.txt")  # noqua
        repo.list_as_objs()[0].key == datamapline_list_objects[0].key


def test_template_zip_repo(templates_zipped):
    templates = extract_zip_file_to_tmpdir(templates_zipped)
    for t in list(templates):
        assert "test_" in t.name

# type: ignore

import tempfile
import json
import os
import pathlib
import zipfile

from typing import List

import pytest
from openpyxl import load_workbook



from engine.exceptions import DatamapNotCSVException
from engine.repository.datamap import InMemorySingleDatamapRepository


def test_datamapline_repository_single_file_repo(datamap, datamapline_list_objects):
    repo = InMemorySingleDatamapRepository(datamap)
    assert repo.list_as_objs()[0].key == datamapline_list_objects[0].key
    assert repo.list_as_objs()[0].sheet == datamapline_list_objects[0].sheet
    assert json.loads(repo.list_as_json())[0]["key"] == "Project/Programme Name"


def test_datamapline_repository_non_existant_file(datamapline_list_objects):
    with pytest.raises(DatamapNotCSVException):
        repo = InMemorySingleDatamapRepository("non-file.txt")  # noqua
        repo.list_as_objs()[0].key == datamapline_list_objects[0].key


def extract_zip_file_to_tmpdir(zfile) -> List[pathlib.Path]:
    tmp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zfile, "r") as zf:
        zf.extractall(tmp_dir)
        return [pathlib.Path(tmp_dir) / x for x in os.listdir(tmp_dir)]


def test_template_zip_repo(templates_zipped):
    templates = extract_zip_file_to_tmpdir(templates_zipped)
    for t in templates:
        assert "test_" in t.name

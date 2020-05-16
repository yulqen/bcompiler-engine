# type: ignore

import json

import pytest

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

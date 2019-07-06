import pytest

from bcompilerengine.main import (DatamapLineType, datamap_reader,
                                  get_cell_data, template_reader)

# def test_datamap_reader():
#    dm_file = "/home/lemon/Documents/bcompiler/datamap.csv"
#    datamap_reader(dm_file)

NUMBER = DatamapLineType.NUMBER


@pytest.fixture
def template():
    return "/home/lemon/Documents/bcompiler/template.xlsx"


def test_template_reader(template):
    data = template_reader(template)
    assert get_cell_data(template, data, "Resource", "C7").value == 0.5
    assert get_cell_data(template, data, "Resource", "C7").cell_type == NUMBER


def test_certain_cell_is_an_integer():
    pass

import datetime
import os

import pytest

from engine.parser import (DatamapLineType, datamap_reader, get_cell_data,
                           template_reader)

NUMBER = DatamapLineType.NUMBER
DATE = DatamapLineType.DATE
STRING = DatamapLineType.STRING

# def test_datamap_reader():
#    dm_file = "/home/lemon/Documents/bcompiler/datamap.csv"
#    datamap_reader(dm_file)


@pytest.fixture
def template():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/test_template.xlsx")


def test_template_reader(template):
    data = template_reader(template)
    assert get_cell_data(data, "Summary", "B2").cell_type == DATE
    assert get_cell_data(data, "Summary", "B3").cell_type == STRING
    assert get_cell_data(data, "Summary", "B4").cell_type == NUMBER
    assert get_cell_data(data, "Summary", "B5").cell_type == NUMBER

    assert get_cell_data(data, "Summary",
                         "B2").value == datetime.datetime(2019, 10, 20, 0, 0)
    assert get_cell_data(data, "Summary", "B3").value == "This is a string"
    assert get_cell_data(data, "Summary", "B4").value == 2.2
    assert get_cell_data(data, "Summary", "B4").value == 2.20
    assert get_cell_data(data, "Summary", "B4").value != 2.21
    assert get_cell_data(data, "Summary", "B5").value == 10

    assert get_cell_data(data, "Another Sheet", "K25").value == "Float:"
    assert get_cell_data(data, "Another Sheet", "K25").cell_type == STRING

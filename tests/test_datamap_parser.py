import datetime

from engine.domain.datamap import DatamapLineValueType
from engine.use_cases.parsing import datamap_reader, template_reader
from engine.utils.extraction import get_cell_data

NUMBER = DatamapLineValueType.NUMBER
DATE = DatamapLineValueType.DATE
TEXT = DatamapLineValueType.TEXT


def test_datamap_reader(datamap):
    data = datamap_reader(datamap)
    assert data[0].key == "Project/Programme Name"
    assert data[0].sheet == "Introduction"
    assert data[0].cellref == "C11"
    assert data[0].filename == datamap


def test_bad_spacing_in_datamap(datamap):
    data = datamap_reader(datamap)
    assert data[14].key == "Bad Spacing"
    assert data[14].sheet == "Introduction"
    assert data[14].cellref == "C35"
    assert data[14].data_type == "DATE"


def test_template_reader(template):
    data = template_reader(template)
    assert get_cell_data(template, data, "Summary",
                         "B2")["data_type"] == "DATE"
    assert get_cell_data(template, data, "Summary",
                         "B3")["data_type"] == "TEXT"
    assert get_cell_data(template, data, "Summary",
                         "B4")["data_type"] == "NUMBER"
    assert get_cell_data(template, data, "Summary",
                         "B5")["data_type"] == "NUMBER"
    assert get_cell_data(template, data, "Summary",
                         "B2")["value"] == datetime.datetime(
                             2019, 10, 20, 0, 0)
    assert get_cell_data(template, data, "Summary",
                         "B3")["value"] == "This is a string"
    assert get_cell_data(template, data, "Summary", "B4")["value"] == 2.2
    assert get_cell_data(template, data, "Summary", "B4")["value"] == 2.20
    assert get_cell_data(template, data, "Summary", "B4")["value"] != 2.21
    assert get_cell_data(template, data, "Summary", "B5")["value"] == 10

    assert get_cell_data(template, data, "Another Sheet",
                         "K25")["value"] == "Float:"
    assert get_cell_data(template, data, "Another Sheet",
                         "K25")["data_type"] == "TEXT"

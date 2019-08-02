import pytest

from engine.domain.datamap import DatamapLineValueType
from engine.use_cases.parsing import datamap_reader, template_reader
from engine.utils.extraction import _get_cell_data

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
    assert data[14].data_type == "TEXT"


def test_template_reader(template) -> None:
    data = template_reader(template)
    assert _get_cell_data(template, data, "Summary", "B2")["data_type"] == "DATE"
    assert _get_cell_data(template, data, "Summary", "B3")["data_type"] == "TEXT"
    assert _get_cell_data(template, data, "Summary", "B4")["data_type"] == "NUMBER"
    assert _get_cell_data(template, data, "Summary", "B5")["data_type"] == "NUMBER"
    assert (
        _get_cell_data(template, data, "Summary", "B2")["value"]
        == "2019-10-20T00:00:00"
    )
    assert (
        _get_cell_data(template, data, "Summary", "B3")["value"] == "This is a string"
    )
    assert _get_cell_data(template, data, "Summary", "B4")["value"] == 2.2
    assert _get_cell_data(template, data, "Summary", "B4")["value"] == 2.20
    assert _get_cell_data(template, data, "Summary", "B4")["value"] != 2.21
    assert _get_cell_data(template, data, "Summary", "B5")["value"] == 10

    assert _get_cell_data(template, data, "Another Sheet", "K25")["value"] == "Float:"
    assert _get_cell_data(template, data, "Another Sheet", "K25")["data_type"] == "TEXT"


def test_incorrect_headers_are_coerced_or_flagged(datamap_moderately_bad_headers):
    data = datamap_reader(datamap_moderately_bad_headers)
    # using same test as above because even though this datamap file has bad keys, we
    # accept them because they are not too bad...
    assert data[14].key == "Bad Spacing"
    assert data[14].sheet == "Introduction"
    assert data[14].cellref == "C35"
    assert data[14].data_type == "TEXT"


def test_very_bad_headers_are_rejected(datamap_very_bad_headers):
    "We want the datamap to be checked first and rejected if the headers are bad"
    with pytest.raises(IndexError):
        data = datamap_reader(datamap_very_bad_headers) # noqa


def test_datamap_type_is_optional(datamap_no_type_col):
    """We want the datamap to be processed even if it doesn't have a type col, which
    should be optional.
    """
    data = datamap_reader(datamap_no_type_col)
    assert data[14].key == "Bad Spacing"
    assert data[14].sheet == "Introduction"
    assert data[14].cellref == "C35"
    assert data[14].data_type is None


def test_datamap_with_only_single_header_raises_exception(datamap_single_header):
    "We want the datamap to be checked first and rejected if the headers are bad"
    with pytest.raises(IndexError):
        data = datamap_reader(datamap_single_header) # noqa

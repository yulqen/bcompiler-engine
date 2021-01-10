import pytest

from pathlib import Path

from engine.domain.datamap import DatamapLineValueType
from engine.utils.extraction import max_tmpl_row
from engine.exceptions import (
    DatamapFileEncodingError,
    MalFormedCSVHeaderException,
    MissingCellKeyError,
    MissingSheetFieldError,
)
from engine.utils.extraction import _get_cell_data, datamap_reader, template_reader

NUMBER = DatamapLineValueType.NUMBER
DATE = DatamapLineValueType.DATE
TEXT = DatamapLineValueType.TEXT


def test_datamap_file_as_pathlib_object(datamap):
    data = datamap_reader(Path(datamap))
    assert len(data) == 18


@pytest.mark.parametrize(
    "datamap_csv_unsupported_encodings",
    [
        "datamap_unicode_text.csv",
        "datamap_note_pad_unicode.csv",
        "datamap_note_pad_unicode_big_endian.csv",
        "datamap_note_pad_utf8.csv",
        "datamap_UTF8.csv",
    ],
    indirect=True,
)
def test_datamap_reader_unsupported_encodings(datamap_csv_unsupported_encodings):
    with pytest.raises(DatamapFileEncodingError):
        _ = datamap_reader(datamap_csv_unsupported_encodings)


@pytest.mark.parametrize(
    "datamap_csv_supported_encodings",
    [
        "datamap_comma_delimited.csv",
        "datamap_macintosh.csv",
        "datamap_msdos.csv",
        "datamap_note_pad_ansi.csv",
        # "datamap_note_pad_ansi.txt", #  We do not currently support .txt files, even if in csv format. Confusing.
    ],
    indirect=True,
)
def test_datamap_reader_supported_encodings(datamap_csv_supported_encodings):
    data = datamap_reader(datamap_csv_supported_encodings)
    assert data[0].key == "Project/Programme Name"
    assert data[0].sheet == "Introduction"
    assert data[0].cellref == "C11"
    assert data[0].filename == str(datamap_csv_supported_encodings)


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
    with pytest.raises(MalFormedCSVHeaderException):
        data = datamap_reader(datamap_very_bad_headers)  # noqa


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
    with pytest.raises(MalFormedCSVHeaderException) as excinfo:
        data = datamap_reader(datamap_single_header)  # noqa
    msg = excinfo.value.args[0]
    assert (
        msg
        == "Datamap contains only one header - need at least three to proceed. Quitting."
    )


def test_datamap_with_two_headers(datamap_two_headers):
    with pytest.raises(MalFormedCSVHeaderException) as excinfo:
        data = datamap_reader(datamap_two_headers)  # noqa
    msg = excinfo.value.args[0]
    assert (
        msg
        == "Datamap contains only two headers - need at least three to proceed. Quitting."
    )


def test_datamap_with_three_headers(datamap_three_headers):
    """
    Should pass because fourth col (type) is optional.
    """
    data = datamap_reader(datamap_three_headers)
    assert data[14].key == "Bad Spacing"
    assert data[14].sheet == "Introduction"
    assert data[14].cellref == "C35"
    assert data[14].data_type is None


def test_datamap_missing_sheet_fields(datamap_missing_fields):
    """We do not want the datamap read to pass if a line has a missing sheet field."""
    with pytest.raises(MissingSheetFieldError):
        data = datamap_reader(datamap_missing_fields)  # noqa


def test_datamap_missing_key_fields(datamap_missing_key_fields):
    """We do not want the datamap read to pass if a line has a missing key field."""
    with pytest.raises(MissingCellKeyError):
        data = datamap_reader(datamap_missing_key_fields)  # noqa


def test_get_file_suffix_from_path(datamap):
    assert datamap.suffix == ".csv"


def test_max_row_for_sheet_according_to_datamap(datamap):
    assert max_tmpl_row(datamap).get("Introduction") == 35
    assert max_tmpl_row(datamap).get("Summary") == 3
    assert max_tmpl_row(datamap).get("Another Sheet") == 39
    assert max_tmpl_row(datamap).get("Non existant sheet") is None

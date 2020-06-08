import zipfile
from pathlib import Path

import pytest
from lxml import etree
from openpyxl import load_workbook

from engine.parser.reader import SpreadsheetReader


@pytest.fixture
def xml_test_file() -> Path:
    return Path.cwd() / "tests" / "resources" / "test.xml"


def test_basic_xml_read(xml_test_file):
    tree = etree.parse(str(xml_test_file))
    assert (
        tree.getroot().tag
        == "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}workbook"
    )


def test_excel_reader_class(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert isinstance(reader.archive, zipfile.ZipFile)


def test_excel_reader_class_file_list(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert "xl/workbook.xml" in reader.valid_files


def test_excel_reader_class_has_package(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert "/xl/worksheets/sheet22.xml" in reader.worksheet_files


def test_excel_reader_class_can_get_sheet_names(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert reader.sheet_names[0] == "Introduction"


def test_excel_reader_class_can_get_shared_strings(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert reader.shared_strings[0] == "Fantastic Portfolio Collection Sheet"


def test_excel_reader_class_can_get_rel_for_worksheet(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert reader._get_sheet_rId("Introduction") == "rId3"
    assert reader._get_sheet_rId("Contents") == "rId4"


def test_excel_reader_class_can_get_worksheet_path_from_rId(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert reader._get_worksheet_path_from_rId("rId3") == "worksheets/sheet1.xml"


def test_get_cell_value_for_cellref_sheet_lxml(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = SpreadsheetReader(tmpl_file)
    assert reader.get_cell_value("C10", "Introduction") == "Coal Tits Ltd"
    assert (
        reader.get_cell_value("C9", "Introduction")
        == "Institute of Hairdressing Dophins"
    )


def test_get_call_value_for_cellref_sheet_lxml_when_value_from_formula(
    org_test_files_dir,
):
    # TODO
    pass


def test_return_suitable_value_when_cell_is_empty(org_test_files_dir):
    # TODO
    pass


@pytest.mark.skip("used for exploring openpyxl")
def test_straight_read_using_openpyxl(org_test_files_dir):
    """The test template file here is full-sized and full of formatting.

    load_workbook() is very slow. Run with --profile
    """
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    breakpoint()
    data = load_workbook(tmpl_file)

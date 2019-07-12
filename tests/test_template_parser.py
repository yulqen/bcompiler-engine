import os
from pathlib import Path

import pytest

from engine.domain.datamap import DatamapLineValueType
from engine.parser import (TemplateCell, _extract_cellrefs, _extract_sheets,
                           get_xlsx_files, parse_multiple_xlsx_files,
                           template_reader)


def test_parse_multiple_templates(resources):
    list_of_template_paths = get_xlsx_files(resources)
    for template in list_of_template_paths:
        if Path(os.path.join(resources, "test_template.xlsx")) == template:
            return True
        else:
            return False


def test_raise_exception_when_none_abs_path_passed():
    with pytest.raises(RuntimeError):
        list_of_template_paths = get_xlsx_files("tests/resources/")  # noqa


def test_func_to_get_sheetnames_as_keys_from_list_of_tcs():
    tc1 = TemplateCell("test_file", "Sheet1", "A1", "test_value1",
                       DatamapLineValueType.TEXT)
    tc2 = TemplateCell("test_file", "Sheet2", "A2", "test_value2",
                       DatamapLineValueType.TEXT)
    tc3 = TemplateCell("test_file", "Sheet2", "A3", "test_value3",
                       DatamapLineValueType.TEXT)
    tc3_dup = TemplateCell("test_file", "Sheet3", "A3", "test_value3",
                           DatamapLineValueType.TEXT)
    xs = [tc3, tc2, tc3_dup, tc1]  # noqa
    assert "Sheet1" in _extract_sheets(xs).keys()
    assert "Sheet2" in _extract_sheets(xs).keys()
    assert "Sheet3" in _extract_sheets(xs).keys()
    assert len(_extract_sheets(xs)["Sheet2"]) == 2
    assert len(_extract_sheets(xs).keys()) == 3


def test_func_to_get_cellrefs_as_keys_from_list_of_tcs():
    tc1 = TemplateCell("test_file", "Shee1", "A1", "test_value1",
                       DatamapLineValueType.TEXT)
    tc2 = TemplateCell("test_file", "Shee1", "A2", "test_value2",
                       DatamapLineValueType.TEXT)
    tc4 = TemplateCell("test_file", "Shee1", "A4", "test_value3",
                       DatamapLineValueType.TEXT)
    xs = [tc4, tc2, tc1]  # noqa
    assert "A1" in _extract_cellrefs(xs).keys()
    assert "A2" in _extract_cellrefs(xs).keys()
    assert "A4" in _extract_cellrefs(xs).keys()
    assert len(_extract_cellrefs(xs).keys()) == 3


def test_template_reader(template):
    dataset = template_reader(template)
    assert (dataset["test_template.xlsx"]["data"]["Summary"]["B3"].value ==
            "This is a string")


def test_extract_data_from_multiple_files_into_correct_structure(resources):
    xlsx_files = get_xlsx_files(resources)
    dataset = parse_multiple_xlsx_files(xlsx_files)
    test_filename = "test_template2.xlsx"
    assert (dataset[test_filename]["data"]["Summary"]["B3"].file_name.name ==
            "test_template2.xlsx")
    assert dataset[test_filename]["data"]["Summary"][
        "B3"].value == "This is a string"

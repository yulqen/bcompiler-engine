import os
from pathlib import Path

import pytest

from engine.parser import get_xlsx_files, parse_multiple_xlsx_files


@pytest.fixture
def resources():
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/"))


def test_parse_multiple_templates(resources):
    list_of_template_paths = get_xlsx_files(resources)
    for template in list_of_template_paths:
        if Path(os.path.join(resources, "test_template.xlsx")) == template:
            return True
        else:
            return False


def test_raise_exception_when_none_abs_path_passed():
    with pytest.raises(RuntimeError):
        list_of_template_paths = get_xlsx_files("tests/resources/")


def test_can_parse_multiple_xlsx_files(resources):
    xlsx_files = get_xlsx_files(resources)
    dataset = parse_multiple_xlsx_files(xlsx_files)
    store_filenames = []
    for x in dataset:
        # we want to store the file names at this stage
        store_filenames.append(x[0].file_name.as_posix())
    for file in xlsx_files:
        # test that we are getting the file names that we expect
        assert file.as_posix() in store_filenames
    for file in xlsx_files:
        if file.name == "test_template2.xlsx":
            test_file = file.as_posix()
    # we want to go through the set of parsed data, for each file
    # and first find the one we want (test_template2.xlsx)...
    for file_data in dataset:
        for cell_lst in file_data:
            if cell_lst.file_name.as_posix() == test_file:
                # then go through the data for that file
                # to find the cell values we want to test
                for tc in file_data:
                    if tc.cell_ref == "C5" and tc.sheet_name == "Summary":
                        assert tc.value == "MEGA VALUE"
                        break
                else:
                    continue
                break
        else:
            continue
        break

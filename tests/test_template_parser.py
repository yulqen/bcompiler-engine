import os
from pathlib import Path

import pytest

from engine.parser import get_xlsx_files


def test_parse_multiple_templates():
    here = os.path.abspath(os.curdir)
    resources = Path(os.path.join(here, "tests/resources/"))
    list_of_template_paths = get_xlsx_files(resources)
    for template in list_of_template_paths:
        if Path(os.path.join(resources, "test_template.xlsx")) == template:
            return True
        else:
            return False


def test_raise_exception_when_none_abs_path_passed():
    with pytest.raises(RuntimeError):
        list_of_template_paths = get_xlsx_files("tests/resources/")

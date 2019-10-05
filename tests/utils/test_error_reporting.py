# test_error_reporting.py

import os
import shutil
from pathlib import Path

from engine.utils.extraction import Check, CheckType, check_datamap_sheets


""""
Tests in here to test ensure that files are checked for integrity before importing
and exporting occurs.
"""


def test_template_checked_for_correct_sheets_which_fails(mock_config, resources):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    mock_config.initialise()
    for fl in os.listdir(resources):
        if fl == "test_template.xlsx" or fl == "datamap.csv":
            shutil.copy(
                Path.cwd() / "tests" / "resources" / fl,
                (Path(mock_config.PLATFORM_DOCS_DIR) / "input"),
            )
    template = Path(mock_config.PLATFORM_DOCS_DIR) / "input" / "test_template.xlsx"
    datamap = Path(mock_config.PLATFORM_DOCS_DIR) / "input" / "datamap.csv"
    check_status = check_datamap_sheets(datamap, template)
    assert isinstance(check_status, Check)
    assert check_status.state == CheckType.FAIL
    assert check_status.error_type == CheckType.MISSING_SHEETS_REQUIRED_BY_DATAMAP
    assert check_status.msg == "File /tmp/Documents/datamaps/input/test_template.xlsx has no sheet[s] Introduction"
    assert check_status.proceed is False


def test_template_checked_for_correct_sheets_which_passes(mock_config, datamap, template_with_introduction_sheet):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    mock_config.initialise()
    check_status = check_datamap_sheets(datamap, template_with_introduction_sheet)
    assert isinstance(check_status, Check)
    assert check_status.state == CheckType.PASS
    assert check_status.msg == "Checked OK."
    assert check_status.proceed is True

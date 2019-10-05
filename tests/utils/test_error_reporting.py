# test_error_reporting.py

import os
import shutil
from pathlib import Path

import pytest

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
    # Because there is no Introduction sheet in template data (template_dict) - should return a fail check
    datamap_lst = [
        {
            "cellref": "C11",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project/Programme Name",
            "sheet": "Introduction",
        },
        {
            "cellref": "C9",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Department",
            "sheet": "Introduction",
        },
        {
            "cellref": "C10",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Delivery Body",
            "sheet": "Introduction",
        },
        {
            "cellref": "C12",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "TOFGM - TUI ID Number",
            "sheet": "Introduction",
        },
        {
            "cellref": "C13",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Controls Project ID number",
            "sheet": "Introduction",
        },
        {
            "cellref": "C14",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project Type (for TUI use)",
            "sheet": "Introduction",
        },
    ]
    template_dict = {
        "filename.xlsm": {
            "data": {
                "To DO": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "To DO",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "To DO",
                        "value": "then update that",
                    },
                },
                "Rich Tea": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "then update that",
                    },
                },
            }
        },
        "filename2.xlsm": {
            "data": {
                "To DO": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "To DO",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "To DO",
                        "value": "then update that",
                    },
                },
                "Rich Tea": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "then update that",
                    },
                },
            }
        },
    }
    check_status = check_datamap_sheets(datamap_lst, template_dict)
    for f in check_status.keys():
        assert check_status[f].state == CheckType.FAIL
        assert (
            check_status[f].error_type
            == CheckType.MISSING_SHEETS_REQUIRED_BY_DATAMAP
        )
        assert (
            check_status[f].msg
            == f"File {f} has no sheet[s] Introduction."
        )
        assert check_status[f].proceed is False


@pytest.mark.skip("Until test above passes")
def test_template_checked_for_correct_sheets_which_passes(mock_config, resources):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    mock_config.initialise()
    for fl in os.listdir(resources):
        if fl == "test_template_with_introduction_sheet.xlsm" or fl == "datamap.csv":
            shutil.copy(
                Path.cwd() / "tests" / "resources" / fl,
                (Path(mock_config.PLATFORM_DOCS_DIR) / "input"),
            )
    template = (
        Path(mock_config.PLATFORM_DOCS_DIR)
        / "input"
        / "test_template_with_introduction_sheet.xlsm"
    )
    datamap = Path(mock_config.PLATFORM_DOCS_DIR) / "input" / "datamap.csv"
    check_status = check_datamap_sheets(datamap, template)
    assert isinstance(check_status, Check)
    assert check_status.state == CheckType.PASS
    assert (
        check_status.msg
        == "Checked /tmp/Documents/datamaps/input/test_template_with_introduction_sheet.xlsm: OK."
    )
    assert check_status.proceed is True

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


def test_template_checked_for_correct_sheets_which_fails(
    mock_config, resources, datamap_lst_with_single_sheet, template_dict
):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    # Because there is no Introduction sheet in template data (template_dict) - should return a fail check
    check_status = check_datamap_sheets(datamap_lst_with_single_sheet, template_dict)
    for f in check_status.keys():
        assert check_status[f].state == CheckType.FAIL
        assert (
            check_status[f].error_type == CheckType.MISSING_SHEETS_REQUIRED_BY_DATAMAP
        )
        assert check_status[f].msg == f"File {f} has no sheet[s] Introduction."
        assert check_status[f].proceed is False


def test_template_checked_for_correct_sheets_which_passes(
    mock_config, resources, datamap_lst_with_sheets_same_as_template_dict, template_dict
):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    check_status = check_datamap_sheets(
        datamap_lst_with_sheets_same_as_template_dict, template_dict
    )
    for f in check_status.keys():
        assert check_status[f].state == CheckType.PASS
        assert (
            check_status[f].error_type == CheckType.UNDEFINED
        )
        assert check_status[f].msg == f"File {f} checked: OK."
        assert check_status[f].proceed is True

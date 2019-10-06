# test_error_reporting.py


import pytest

from engine.exceptions import RemoveFileWithNoSheetRequiredByDatamap
from engine.utils.extraction import (CheckType, check_datamap_sheets,
                                     remove_failing_files)


""""
Tests in here to test ensure that files are checked for integrity before importing
and exporting occurs.
"""


def test_template_checked_for_correct_sheets_which_fails(
    datamap_lst_with_single_sheet, template_dict
):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    # Because there is no Introduction sheet in template data (template_dict) - should return a fail check
    check_status = check_datamap_sheets(datamap_lst_with_single_sheet, template_dict)
    for f in check_status:
        assert f.state == CheckType.FAIL
        assert f.error_type == CheckType.MISSING_SHEETS_REQUIRED_BY_DATAMAP
        assert f.msg == f"File {f.filename} has no sheet[s] Introduction."
        assert f.proceed is False


def test_template_checked_for_correct_sheets_which_passes(
    datamap_lst_with_sheets_same_as_template_dict, template_dict
):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    check_status = check_datamap_sheets(
        datamap_lst_with_sheets_same_as_template_dict, template_dict
    )
    for f in check_status:
        assert f.state == CheckType.PASS
        assert f.error_type == CheckType.UNDEFINED
        assert f.msg == f"File {f.filename} checked: OK."
        assert f.proceed is True


def test_remove_file_data_from_template_data_structure_if_failing_sheets_test(
    datamap_lst_with_single_sheet, template_dict
):
    with pytest.raises(RemoveFileWithNoSheetRequiredByDatamap):
        check_status = check_datamap_sheets(datamap_lst_with_single_sheet, template_dict)
        template_dict = remove_failing_files(check_status, template_dict)

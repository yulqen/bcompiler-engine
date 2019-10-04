# test_error_reporting.py

from engine.utils.extraction import Check, CheckType, check_datamap_sheets


""""
Tests in here to test ensure that files are checked for integrity before importing
and exporting occurs.
"""


def test_template_checked_for_correct_sheets_which_fails(datamap, template):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    check_status = check_datamap_sheets(datamap, template)
    assert isinstance(check_status, Check)
    assert check_status.state == CheckType.FAIL
    assert check_status.error_type == CheckType.MISSING_SHEET_REQUIRED_BY_DATAMAP
    assert check_status.msg == "File test_template.xlsx has no sheet[s] Introduction"
    assert check_status.proceed is False


def test_template_checked_for_correct_sheets_which_passes(datamap, template_with_introduction_sheet):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    check_status = check_datamap_sheets(datamap, template_with_introduction_sheet)
    assert isinstance(check_status, Check)
    assert check_status.state == CheckType.PASS
    assert check_status.msg == "Checked OK."
    assert check_status.proceed is True

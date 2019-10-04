# test_error_reporting.py

from engine.utils.extraction import Check, CheckType, check_datamap_sheets


""""
Tests in here to test ensure that files are checked for integrity before importing
and exporting occurs.
"""


def test_template_checked_for_correct_sheets(datamap, template):
    """
    Function under test should notify if a template does not have all the
    sheets included in the datamap.
    """
    result = check_datamap_sheets(datamap, template)
    assert isinstance(result, Check)
    assert result.state == CheckType.FAIL
    assert result.error_type == CheckType.MISSING_SHEET_REQUIRED_BY_DATAMAP
    assert result.msg == "File test_template.xlsx has no sheet[s] Introduction"
    assert result.proceed is False

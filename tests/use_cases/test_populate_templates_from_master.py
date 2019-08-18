"""
Test the processes involved in populating a bunch of blank
templates with data from a single master file.
"""

from openpyxl import load_workbook

from engine.repository.templates import MultipleTemplatesWriteRepo
from engine.use_cases.output import WriteMasterToTemplates


def test_output_gateway(mock_config, datamap, master, blank_template):
    output_repo = MultipleTemplatesWriteRepo(mock_config)
    uc = WriteMasterToTemplates(output_repo, datamap, master, blank_template)
    uc.execute()
    result_file = mock_config.PLATFORM_DOCS_DIR / "output" / "Chutney Bridge.xlsm"
    wb = load_workbook(result_file)
    intro_sheet = wb.get_sheet_by_name("Introduction")
    assert intro_sheet["C9"] == "Accounting Department"

"""
Test the processes involved in populating a bunch of blank
templates with data from a single master file.
"""

import datetime

from openpyxl import load_workbook

from engine.repository.templates import MultipleTemplatesWriteRepo
from engine.use_cases.output import WriteMasterToTemplates


def test_output_gateway(mock_config, datamap, master, blank_template):
    mock_config.initialise()
    output_dir = mock_config.PLATFORM_DOCS_DIR / "output"
    output_repo = MultipleTemplatesWriteRepo(output_dir, blank_template)
    uc = WriteMasterToTemplates(output_repo, datamap, master, blank_template)
    uc.execute()
    result_file = mock_config.PLATFORM_DOCS_DIR / "output" / "Chutney Bridge.xlsm"
    wb = load_workbook(result_file)
    intro_sheet = wb["Introduction"]
    summ_sheet = wb["Summary"]
    an_sheet = wb["Another Sheet"]
    assert intro_sheet["C9"].value == "Accounting Department"
    assert intro_sheet["C10"].value == "Satellite Corp"
    assert intro_sheet["C13"].value == 1334
    # note that dates come out of spreadsheets as datetime objects
    assert intro_sheet["C17"].value == datetime.datetime(2012, 1, 1, 0, 0)
    assert summ_sheet["B3"].value == "Bobbins"
    assert an_sheet["F17"].value == 20.303
    # note that dates come out of spreadsheets as datetime objects
    assert an_sheet["H39"].value == datetime.datetime(2024, 2, 1, 0, 0)

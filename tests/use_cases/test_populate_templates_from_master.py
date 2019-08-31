"""
Test the processes involved in populating a bunch of blank
templates with data from a single master file.
"""

import datetime

from openpyxl import Workbook, load_workbook

from engine.repository.templates import MultipleTemplatesWriteRepo
from engine.use_cases.output import WriteMasterToTemplates

#from openpyxl.worksheet.datavalidation import DataValidation


# NOT INCLUDED IN TESTS - FOR PROVING DATA VALIDATION
#def test_write_simple_data_validation_into_file():
#    wb = Workbook()
#    ws = wb.active
#    dv = DataValidation(type="list", formula1='"Trumpet,Piano"', allow_blank=True)
#    ws.add_data_validation(dv)
#    dv.add("A1:B20")
#    wb.save("/tmp/tosser.xlsx")
#
#


def test_get_all_data_validation_in_sheet(blank_org_template):
    breakpoint()
    wb = load_workbook(blank_org_template)
    ws = wb["1 - Project Info"]
    validations = ws.data_validations.dataValidation


def test_output_gateway(mock_config, datamap, master, blank_template):
    mock_config.initialise()
    output_repo = MultipleTemplatesWriteRepo(blank_template)
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

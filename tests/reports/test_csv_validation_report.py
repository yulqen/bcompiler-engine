import csv
import shutil
import pytest
from pathlib import Path

from engine.use_cases.parsing import (
    validation_checker,
    CreateMasterUseCaseWithValidation,
)
from engine.reports.validation import ValidationReportCSV, ValidationCheck
from engine.repository.templates import (
    InMemoryPopulatedTemplatesRepository,
)
from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.repository.master import MasterOutputRepository


def test_compare_datamap_data_with_template_data():
    dm_data = [
        {
            "key": "Date Key",
            "sheet": "Summary",
            "cellref": "A1",
            "data_type": "DATE",
            "filename": "/home/lemon/code/python/bcompiler-engine/ \
                tests/resources/datamap_match_test_template.csv",
        },
        {
            "key": "String Key",
            "sheet": "Summary",
            "cellref": "A2",
            "data_type": "TEXT",
            "filename": "/home/lemon/code/python/bcompiler-engine/ \
                    tests/resources/datamap_match_test_template.csv",
        },
    ]
    tmp_data = {
        "test_template.xlsx": {
            "checksum": "fjfj34jk22l134hl",
            "data": {
                "Summary": {
                    "A1": {
                        "cell_ref": "A1",
                        "file_name": "test_template.xlsx",
                        "sheet": "Summary",
                        "value": "2020-12-02",
                        "data_type": "DATE",
                    },
                    "A2": {
                        "cell_ref": "A2",
                        "file_name": "test_template.xlsx",
                        "sheet": "Summary",
                        "value": 2,
                        "data_type": "NUMBER",
                    },
                },
            },
        },
    }
    checks = validation_checker(dm_data, tmp_data)
    assert len(checks) == 2
    assert checks[0].passes is True
    assert checks[0].filename == "test_template.xlsx"
    assert checks[0].sheetname == "Summary"
    assert checks[0].cellref == "A1"
    assert checks[0].wanted == "DATE"
    assert checks[0].got == "DATE"
    assert checks[1].passes is False


def test_create_master_spreadsheet_with_validation(
    mock_config, datamap_match_test_template, template
):
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap_match_test_template)
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCaseWithValidation(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")
    # FIXME - this is not a good test; no assurance about ordering in a list
    assert uc.final_validation_checks[0].passes is True


def test_csv_validation_report_writer(mock_config):
    mock_config.initialise()
    validation_data = [
        ValidationCheck(
            passes=bool,
            filename="toss.xlsx",
            value="Burgers",
            cellref="A1",
            sheetname="Chopper",
            wanted="TEXT",
            got="TEXT",
        ),
        ValidationCheck(
            passes=bool,
            filename="toss.xlsx",
            value="Burgers & Chips",
            cellref="A2",
            sheetname="Chopper",
            wanted="TEXT",
            got="NUMBER",
        ),
        ValidationCheck(
            passes=bool,
            filename="toss.xlsx",
            value="Ham and grease",
            cellref="A3",
            sheetname="Chopper",
            wanted="TEXT",
            got="DATE",
        ),
    ]
    report = ValidationReportCSV(validation_data).write()
    with open(mock_config.FULL_PATH_OUTPUT / "validation_report.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        first_row = next(reader)
        assert first_row["Filename"] == "toss.xlsx"
        assert first_row["Value"] == "Burgers"
        assert first_row["Cell Reference"] == "A1"
        assert first_row["Expected Type"] == "TEXT"
        assert first_row["Got Type"] == "TEXT"


def test_validation_results_go_to_csv_file(
    mock_config, datamap_match_test_template, template
):
    """
    Validation results should end up in a csv file of the form:

     How do we want the csv report to look?

     Filename,Key,Cell Reference,Expected Type,Got Type
     test_template.xlsx,Date Key,Summary,B2,DATE,DATE
     test_template.xlsx,String Key,Summary,B3,TEXT,TEXT
     test_template.xlsx,Big Float,Another Sheet,F17,NUMBER,NUMBER
     test_template.xlsx,Funny Date,Another Sheet,H39,DATE,NUMBER
    """
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap_match_test_template)
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCaseWithValidation(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")

    # TODO - There is not validation report here yet because we have to write
    # it in the CreateMasterUseCaseWithValidation class
    with open(mock_config.FULL_PATH_OUTPUT / "validation_report.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["Filename"] == "test_template.xlsx"

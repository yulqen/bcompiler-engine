import csv
import shutil
from pathlib import Path

import pytest
from engine.reports.validation import ValidationReportCSV
from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.repository.master import MasterOutputRepository
from engine.repository.templates import InMemoryPopulatedTemplatesRepository
from engine.use_cases.parsing import (
    CreateMasterUseCase,
    CreateMasterUseCaseWithValidation,
)
from engine.utils.validation import (
    ValidationCheck,
    _Typed,
    _TypeMatched,
    _Unvalidated,
    _ValidationComplete,
    _ValidationState,
    _ValueGiven,
    _ValueWanted,
    validate_line,
    validation_checker,
)


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
    assert checks[0].passes == "PASS"
    assert checks[0].filename == "test_template.xlsx"
    assert checks[0].sheetname == "Summary"
    assert checks[0].cellref == "A1"
    assert checks[0].wanted == "DATE"
    assert checks[0].got == "DATE"
    assert checks[1].passes == "FAIL"


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
    assert uc.final_validation_checks[0].passes == "PASS"


def test_csv_validation_report_writer(mock_config):
    mock_config.initialise()
    validation_data = [
        ValidationCheck(
            passes="PASS",
            filename="toss.xlsx",
            key="Test Key 1",
            value="Burgers",
            cellref="A1",
            sheetname="Chopper",
            wanted="TEXT",
            got="TEXT",
        ),
        ValidationCheck(
            passes="PASS",
            filename="toss.xlsx",
            key="Test Key 2",
            value="Burgers & Chips",
            cellref="A2",
            sheetname="Chopper",
            wanted="TEXT",
            got="NUMBER",
        ),
        ValidationCheck(
            passes="PASS",
            filename="toss.xlsx",
            key="Test Key 3",
            value="Ham and grease",
            cellref="A3",
            sheetname="Chopper",
            wanted="TEXT",
            got="DATE",
        ),
    ]
    ValidationReportCSV(validation_data).write()
    pth = mock_config.FULL_PATH_OUTPUT
    f = list(
        pth.glob("*.csv")
    )  # we have to do this because filename includes timestamp
    with open(f[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        first_row = next(reader)
        assert first_row["Pass Status"] == "PASS"
        assert first_row["Filename"] == "toss.xlsx"
        assert first_row["Key"] == "Test Key 1"
        assert first_row["Value"] == "Burgers"
        assert first_row["Cell Reference"] == "A1"
        assert first_row["Sheet Name"] == "Chopper"
        assert first_row["Expected Type"] == "TEXT"
        assert first_row["Got Type"] == "TEXT"


def test_validation_results_go_to_csv_file(
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

    pth = mock_config.FULL_PATH_OUTPUT
    f = list(
        pth.glob("*.csv")
    )  # we have to do this because filename includes timestamp
    with open(f[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        assert (
            row["Filename"]
            == f"{str(mock_config.PLATFORM_DOCS_DIR / 'input')}/test_template.xlsx"
        )
        assert row["Pass Status"] == "PASS"
        assert row["Key"] == "Date Key"
        assert row["Sheet Name"] == "Summary"
        assert row["Expected Type"] == "DATE"


def test_validation_csv_report_contains_fail_state(
    mock_config, datamap_match_test_template, template_incorrect_type
):
    mock_config.initialise()
    shutil.copy2(
        template_incorrect_type, (Path(mock_config.PLATFORM_DOCS_DIR) / "input")
    )
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap_match_test_template)
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCaseWithValidation(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")

    pth = mock_config.FULL_PATH_OUTPUT
    f = list(
        pth.glob("*.csv")
    )  # we have to do this because filename includes timestamp

    with open(f[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        assert (
            row["Filename"]
            == f"{str(mock_config.PLATFORM_DOCS_DIR / 'input')}/test_template_incorrect_type.xlsx"
        )
        assert row["Pass Status"] == "FAIL"
        assert row["Key"] == "Date Key"
        assert row["Sheet Name"] == "Summary"
        assert row["Expected Type"] == "DATE"


def test_validation_csv_report_with_mixture_of_included_types(
    mock_config, datamap_missing_one_type, template
):
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap_missing_one_type)
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCaseWithValidation(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")

    pth = mock_config.FULL_PATH_OUTPUT
    f = list(
        pth.glob("*.csv")
    )  # we have to do this because filename includes timestamp

    with open(f[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        row = next(reader)  # we need the second row
        assert (
            row["Filename"]
            == f"{str(mock_config.PLATFORM_DOCS_DIR / 'input')}/test_template.xlsx"
        )
        assert row["Pass Status"] == "UNTYPED"
        assert row["Key"] == "String Key"
        assert row["Sheet Name"] == "Summary"
        assert row["Expected Type"] == "NA"


def test_skips_type_validation_report_if_no_type_col_in_dm(
    mock_config, datamap_no_type_col_matches_test_template, template
):
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(datamap_no_type_col_matches_test_template)
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCase(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")

    pth = mock_config.FULL_PATH_OUTPUT
    f = list(
        pth.glob("*.csv")
    )  # we have to do this because filename includes timestamp
    assert len(f) == 0


def test_incorrect_validation_type_is_na(
    mock_config, datamap_match_test_template_incorrect_type_descriptor, template
):
    """
    We want to show incorrect wanted types in the validation report so the
    user can fix them.
    """
    mock_config.initialise()
    shutil.copy2(template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(
        datamap_match_test_template_incorrect_type_descriptor
    )
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCaseWithValidation(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")

    pth = mock_config.FULL_PATH_OUTPUT
    f = list(
        pth.glob("*.csv")
    )  # we have to do this because filename includes timestamp

    with open(f[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)
        next(reader)
        row = next(reader)  # we need the third row
        assert row["Expected Type"] == "BUTTER"


def test_empty_cells_in_template_expected_by_dm_go_into_val_report(
    mock_config,
    datamap_match_test_template_with_missing_val_match_template_equiv,
    template_with_empty_cells_expected_by_datamap,
):
    mock_config.initialise()
    shutil.copy2(
        template_with_empty_cells_expected_by_datamap,
        (Path(mock_config.PLATFORM_DOCS_DIR) / "input"),
    )
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        mock_config.PLATFORM_DOCS_DIR / "input"
    )
    dm_repo = InMemorySingleDatamapRepository(
        datamap_match_test_template_with_missing_val_match_template_equiv
    )
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCaseWithValidation(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")

    pth = mock_config.FULL_PATH_OUTPUT
    f = list(
        pth.glob("*.csv")
    )  # we have to do this because filename includes timestamp

    with open(f[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        row = next(reader)
        row = next(reader)
        row = next(reader)
        row = next(reader)  # we want the fifth row
        assert row["Key"] == "Missing Value"
        assert row["Value"] == "NO VALUE RETURNED"
        assert (
            row["Filename"]
            == f"{str(mock_config.PLATFORM_DOCS_DIR / 'input')}/test_template_with_empty_cells_expected_by_datamap.xlsm"
        )
        assert row["Pass Status"] == "FAIL"
        assert row["Sheet Name"] == "Summary"
        assert row["Expected Type"] == "TEXT"
        assert row["Got Type"] == "EMPTY"
        row = next(reader)
        row = next(reader)  # now we want Missing Value 3
        assert row["Key"] == "Missing Value 3"
        assert row["Expected Type"] == "NA"


def test_validation_as_a_state_machine(dm_data, sheet_data):
    v = _ValidationState(dm_data[0], sheet_data)
    assert v.__class__ == _Unvalidated
    v.check()
    assert v.__class__ == _ValueWanted
    v.check()
    assert v.__class__ == _Typed
    v.check()
    assert v.__class__ == _TypeMatched
    v.check()
    assert v.validation_check.passes == "PASS"
    assert v.validation_check.got == dm_data[0]["data_type"]
    assert v.__class__ == _ValueGiven
    v.check()
    assert v.__class__ == _ValidationComplete

    # Now we run it as a loop...
    v = _ValidationState(dm_data[0], sheet_data)
    while True:
        v.check()
        if v.__class__ == _ValidationComplete:
            assert v.validation_check.passes == "PASS"
            assert v.validation_check.filename == v.cell_data["file_name"]
            assert v.validation_check.key == dm_data[0]["key"]
            assert v.validation_check.sheetname == v.cell_data["sheet_name"]
            assert v.validation_check.cellref == dm_data[0]["cellref"]
            assert v.validation_check.cellref == v.cell_data["cellref"]
            assert v.validation_check.value == v.cell_data["value"]
            assert v.validation_check.wanted == dm_data[0]["data_type"]
            assert v.validation_check.got == v.cell_data["data_type"]
            break


@pytest.mark.parametrize(
    "dm_index,dm_data_type,passes,value,wanted,got",
    [
        (0, "", "UNTYPED", "Text Key Value", "NA", "TEXT"),
        (1, "", "UNTYPED", "String Key Value", "NA", "TEXT"),
        (1, "TEXT", "PASS", "String Key Value", "TEXT", "TEXT"),
        (1, "ROBIN", "UNTYPED", "String Key Value", "ROBIN", "TEXT"),
        (2, "NUMBER", "PASS", "Big Float Value", "NUMBER", "NUMBER"),
    ],
)
def test_validation_line_driver(
    dm_data, sheet_data, dm_index, dm_data_type, passes, value, wanted, got
):
    # we use the fixture but change it for this test
    dm_data[dm_index]["data_type"] = dm_data_type
    v_out = validate_line(dm_data[dm_index], sheet_data)
    assert v_out.validation_check.passes == passes
    assert v_out.validation_check.value == value
    assert v_out.validation_check.wanted == wanted
    assert v_out.validation_check.got == got

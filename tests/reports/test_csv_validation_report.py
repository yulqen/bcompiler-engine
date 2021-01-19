import csv
import shutil
from pathlib import Path
from typing import Dict

from engine.reports.validation import ValidationCheck, ValidationReportCSV
from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.repository.master import MasterOutputRepository
from engine.repository.templates import InMemoryPopulatedTemplatesRepository
from engine.use_cases.parsing import (
    CreateMasterUseCase,
    CreateMasterUseCaseWithValidation,
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
    _, checks = validation_checker(dm_data, tmp_data)
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
        assert row["Filename"] == "test_template.xlsx"
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
        assert row["Filename"] == "test_template_incorrect_type.xlsx"
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
        assert row["Filename"] == "test_template.xlsx"
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
            row["Filename"] == "test_template_with_empty_cells_expected_by_datamap.xlsm"
        )
        assert row["Pass Status"] == "FAIL"
        assert row["Sheet Name"] == "Summary"
        assert row["Expected Type"] == "TEXT"
        assert row["Got Type"] == "EMPTY"
        row = next(reader)
        row = next(reader)  # now we want Missing Value 3
        assert row["Key"] == "Missing Value 3"
        assert row["Expected Type"] == "NA"


class ValidationState:
    def __init__(self, dm_line: Dict[str, str], sheet_data):
        self.new_state(Unvalidated)
        self.sheet_data = sheet_data
        self.dm_line = dm_line
        self.cell_data = sheet_data[dm_line["sheet"]][dm_line["cellref"]]
        self.validation_check = ValidationCheck(
            passes="",
            filename=self.cell_data["file_name"],
            key=self.dm_line["key"],
            value="",
            sheetname=self.dm_line["sheet"],
            cellref=self.dm_line["cellref"],
            wanted=self.dm_line["data_type"],
            got="",
        )

    def new_state(self, newstate):
        self.__class__ = newstate

    def check(self):
        raise NotImplementedError()

    def update_validation_check(self):
        raise NotImplementedError()


class Unvalidated(ValidationState):
    def check(self):
        if (
            self.dm_line["sheet"] == list(self.sheet_data.keys())[0]
            and self.dm_line["cellref"] in self.sheet_data[self.dm_line["sheet"]].keys()
        ):
            self.new_state(ValueWanted)
        else:
            self.new_state(ValueUnwanted)


class ValueWanted(ValidationState):
    def check(self):
        if self.dm_line["data_type"] == self.cell_data["data_type"]:
            self.new_state(TypeMatched)
            self.validation_check.got = self.cell_data["data_type"]
        else:
            self.new_state(TypeNotMatched)
            self.validation_check.got = self.cell_data["NA"]


class TypeMatched(ValidationState):
    def check(self):
        if self.cell_data["value"] == "":
            self.new_state(EmptyValue)
        else:
            self.new_state(GivenValue)


class TypeNotMatched(ValidationState):
    def check(self):
        if self.cell_data["value"] == "":
            self.new_state(EmptyValue)
        else:
            self.new_state(GivenValue)


class EmptyValue(ValidationState):
    def check(self):
        ...


class GivenValue(ValidationState):
    def check(self):
        ...


class ValueUnwanted(ValidationState):
    def check(self):
        raise RuntimeError()


class ValidationComplete(ValidationState):
    def check(self):
        print("Validation Complete")


class ValidationFailed(ValidationState):
    def check(self):
        self.new_state(ValidationPassed)


class ValidationPassed(ValidationState):
    def check(self):
        self.new_state(ValidationComplete)


def test_validation_as_a_state_machine():
    dm_data = [
        {
            "cellref": "B2",
            "data_type": "TEXT",
            "filename": "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap_match_test_template.csv",
            "key": "Text Key",
            "sheet": "Summary",
        },
        {
            "cellref": "B3",
            "data_type": "TEXT",
            "filename": "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap_match_test_template.csv",
            "key": "String Key",
            "sheet": "Summary",
        },
        {
            "cellref": "F17",
            "data_type": "NUMBER",
            "filename": "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap_match_test_template.csv",
            "key": "Big Float",
            "sheet": "Summary",
        },
    ]
    tmp_data = {
        "Summary": {
            "B2": {
                "cellref": "B2",
                "data_type": "TEXT",
                "file_name": "/tmp/Documents/datamaps/input/test_template.xlsx",
                "sheet_name": "Summary",
                "value": "Text Key Value",
            },
            "B3": {
                "cellref": "B3",
                "data_type": "TEXT",
                "file_name": "/tmp/Documents/datamaps/input/test_template.xlsx",
                "sheet_name": "Summary",
                "value": "String Key Value",
            },
            "F17": {
                "cellref": "F17",
                "data_type": "NUMBER",
                "file_name": "/tmp/Documents/datamaps/input/test_template.xlsx",
                "sheet_name": "Summary",
                "value": "Big Float Value",
            },
        }
    }

    v = ValidationState(dm_data[0], tmp_data)
    assert v.__class__ == Unvalidated
    v.check()
    assert v.__class__ == ValueWanted
    v.check()
    assert v.__class__ == TypeMatched
    assert v.validation_check.got == dm_data[0]["data_type"]
    v.check()
    assert v.__class__ == GivenValue

import pytest
from engine.utils.validation import validate_line


class TestValidation:
    @pytest.mark.parametrize("data_type", ["TEXT", "NUMBER", "DATE"])
    def test_validation_simple_pass(self, data_type):
        dm_line = {
            "cellref": "A1",
            "data_type": data_type,
            "filename": "datamap.csv",
            "key": "Text Key",
            "sheet": "Sheet A",
        }
        sheet_data = {
            "A1": {
                "cellref": "A1",
                "data_type": data_type,
                "file_name": "chutney.xlsx",
                "key": "Text Key",
                "sheet": "Sheet A",
                "value": "Text Key Value",
            }
        }
        v = validate_line(dm_line, sheet_data)
        assert v.validation_check.passes == "PASS"
        assert v.validation_check.filename == "chutney.xlsx"
        assert v.validation_check.wanted == data_type
        assert v.validation_check.got == data_type

    @pytest.mark.parametrize("data_type", ["BOBBINS", "CHICKEN", "RABBIT"])
    def test_validation_simple_fail_using_disallowed_types(self, data_type):
        dm_line = {
            "cellref": "A1",
            "data_type": data_type,
            "filename": "datamap.csv",
            "key": "Text Key",
            "sheet": "Sheet A",
        }
        sheet_data = {
            "A1": {
                "cellref": "A1",
                "data_type": "TEXT",
                "file_name": "chutney.xlsx",
                "key": "Text Key",
                "sheet": "Sheet A",
                "value": 10,
            }
        }
        v = validate_line(dm_line, sheet_data)
        assert v.validation_check.passes == "UNTYPED"
        assert v.validation_check.filename == "chutney.xlsx"
        assert v.validation_check.wanted == data_type
        assert v.validation_check.got == "TEXT"

    @pytest.mark.parametrize(
        "wanted,got,val",
        [
            ("TEXT", "NUMBER", 10),
            ("NUMBER", "TEXT", "cribbage"),
            ("DATE", "TEXT", "crabbage"),
        ],
    )
    def test_validation_simple_fails(self, wanted, got, val):
        dm_line = {
            "cellref": "A1",
            "data_type": wanted,
            "filename": "datamap.csv",
            "key": "Text Key",
            "sheet": "Sheet A",
        }
        sheet_data = {
            "A1": {
                "cellref": "A1",
                "data_type": got,
                "file_name": "chutney.xlsx",
                "key": "Text Key",
                "sheet": "Sheet A",
                "value": val,
            }
        }
        v = validate_line(dm_line, sheet_data)
        assert v.validation_check.passes == "FAIL"
        assert v.validation_check.filename == "chutney.xlsx"
        assert v.validation_check.wanted == wanted
        assert v.validation_check.got == got
        assert v.validation_check.value == val

    def test_validation_simple_untyped(self):
        dm_line = {
            "cellref": "A1",
            "data_type": "",
            "filename": "datamap.csv",
            "key": "Text Key",
            "sheet": "Sheet A",
        }
        sheet_data = {
            "A1": {
                "cellref": "A1",
                "data_type": "NUMBER",
                "file_name": "chutney.xlsx",
                "key": "Text Key",
                "sheet": "Sheet A",
                "value": 10,
            }
        }
        v = validate_line(dm_line, sheet_data)
        assert v.validation_check.passes == "UNTYPED"
        assert v.validation_check.filename == "chutney.xlsx"
        assert v.validation_check.wanted == "NA"
        assert v.validation_check.got == "NUMBER"

    def test_validation_empty_cells_in_template_expected_by_dm(self):
        dm_line = {
            "cellref": "A1",
            "data_type": "TEXT",
            "filename": "datamap.csv",
            "key": "Text Key",
            "sheet": "Sheet A",
        }
        sheet_data = {
            "NOTEXIST": {  # simulates this line not being present in data sent validation
                "cellref": "A1",
                "data_type": "TEXT",
                "file_name": "chutney.xlsx",
                "key": "Text Key",
                "sheet": "Sheet A",
                "value": "",
            }
        }
        v = validate_line(dm_line, sheet_data)
        assert v.validation_check.passes == "FAIL"
        assert v.validation_check.filename == "chutney.xlsx"
        assert v.validation_check.wanted == "TEXT"
        assert v.validation_check.got == "EMPTY"

    def test_validation_untyped_and_empty_in_template(self):
        dm_line = {
            "cellref": "A1",
            "data_type": "",
            "filename": "datamap.csv",
            "key": "Text Key",
            "sheet": "Sheet A",
        }
        sheet_data = {
            "NOEXIST": {  # simulates this line not being present in data sent validation
                "cellref": "A1",
                "data_type": "",
                "file_name": "chutney.xlsx",
                "key": "Text Key",
                "sheet": "Sheet A",
                "value": "",
            }
        }
        v = validate_line(dm_line, sheet_data)
        assert v.validation_check.passes == "FAIL"
        assert v.validation_check.filename == "chutney.xlsx"
        assert v.validation_check.wanted == "NA"
        assert v.validation_check.got == "EMPTY"

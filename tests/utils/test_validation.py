from engine.utils.validation import validate_line


def test_validation_simple_pass():
    dm_line = {
        "cellref": "A1",
        "data_type": "TEXT",
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
            "value": "Text Key Value"
        }
    }
    v = validate_line(dm_line, sheet_data)
    assert v.validation_check.passes == "PASS"
    assert v.validation_check.filename == "chutney.xlsx"
    assert v.validation_check.wanted == "TEXT"
    assert v.validation_check.got == "TEXT"
    


def test_validation_simple_fail():
    dm_line = {
        "cellref": "A1",
        "data_type": "TEXT",
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
            "value": 10
        }
    }
    v = validate_line(dm_line, sheet_data)
    assert v.validation_check.passes == "FAIL"
    assert v.validation_check.filename == "chutney.xlsx"
    assert v.validation_check.wanted == "TEXT"
    assert v.validation_check.got == "NUMBER"


def test_validation_simple_untyped():
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
            "value": 10
        }
    }
    v = validate_line(dm_line, sheet_data)
    assert v.validation_check.passes == "UNTYPED"
    assert v.validation_check.filename == "chutney.xlsx"
    assert v.validation_check.wanted == "NA"
    assert v.validation_check.got == "NUMBER"


def test_validation_empty_cells_in_template_expected_by_dm():
    dm_line = {
        "cellref": "A1",
        "data_type": "TEXT",
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
            "value": ""
        }
    }
    v = validate_line(dm_line, sheet_data)
    assert v.validation_check.passes == "PASS"
    assert v.validation_check.filename == "chutney.xlsx"
    assert v.validation_check.wanted == "TEXT"
    assert v.validation_check.got == "TEXT"


def test_validation_untyped_and_empty_in_template():
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
            "data_type": "",
            "file_name": "chutney.xlsx",
            "key": "Text Key",
            "sheet": "Sheet A",
            "value": ""
        }
    }
    v = validate_line(dm_line, sheet_data)
    assert v.validation_check.passes == "UNTYPED"
    assert v.validation_check.filename == "chutney.xlsx"
    assert v.validation_check.wanted == "NA"
    assert v.validation_check.got == "NO VALUE RETURNED"

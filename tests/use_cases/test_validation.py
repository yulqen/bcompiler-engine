import shutil
from pathlib import Path

from engine.use_cases.parsing import validation_checker, CreateMasterUseCaseWithValidation
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
            "filename": "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap_match_test_template.csv",
        },
        {
            "key": "String Key",
            "sheet": "Summary",
            "cellref": "A2",
            "data_type": "TEXT",
            "filename": "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap_match_test_template.csv",
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

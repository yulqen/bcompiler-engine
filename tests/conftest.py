import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, List

import pytest

from engine.config import Config
from engine.domain.datamap import DatamapLine, DatamapLineValueType
from engine.domain.template import TemplateCell


@pytest.fixture
def template_cell_obj() -> TemplateCell:
    return TemplateCell(
        file_name="test.xlsx",
        sheet_name="Test Sheet 1",
        cellref="A10",
        value="Test Value",
        data_type=DatamapLineValueType.TEXT,
    )


@pytest.fixture
def datamapline_list_objects() -> List[DatamapLine]:
    dml1 = DatamapLine(
        key="Project/Programme Name",
        sheet="Introduction",
        cellref="C11",
        data_type="TEXT",
        filename="/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",
    )
    dml2 = DatamapLine(
        key="Department",
        sheet="Introduction",
        cellref="C9",
        data_type="TEXT",
        filename="/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",
    )
    dml3 = DatamapLine(
        key="Delivery Body",
        sheet="Introduction",
        cellref="C10",
        data_type="TEXT",
        filename="/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",
    )
    dml4 = DatamapLine(
        key="GMPP - IPA ID Number",
        sheet="Introduction",
        cellref="C12",
        data_type="TEXT",
        filename="/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",
    )
    return [dml1, dml2, dml3, dml4]


@pytest.fixture
def dat_file() -> Path:
    """A data file containing data from a single spreadsheet.

    Uses the data from spreadsheet_same_data_as_dat_file() below
    """
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/extracted_data.dat"))


@pytest.fixture
def spreadsheet_same_data_as_dat_file():
    """A spreadsheet file containing data that is mirrored in dat_file() above"""
    return Path(Path.cwd() / "tests/resources/test_dat_file_use_case.xlsx")


@pytest.fixture
def spreadsheet_one_cell_different_data_than_dat_file():
    "Same as spreadsheet_same_data_as_dat_file() but with cellref newsheet/B5 different"
    return Path(
        Path.cwd()
        / "tests/resources/test_data_file_use_case_diff_data_from_dat_file.xlsx"
    )


@pytest.fixture
def resources() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/"))


@pytest.fixture
def doc_directory():
    pth = Path(tempfile.gettempdir()) / "Documents" / "datamaps"
    yield pth
    shutil.rmtree(pth)


@pytest.fixture
def template_with_introduction_sheet() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(
        os.path.join(here, "tests/resources/test_template_with_introduction_sheet.xlsm")
    )


@pytest.fixture
def template() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/test_template.xlsx"))


@pytest.fixture
def bad_sheet_template() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/bad_sheet_template.xlsm"))


@pytest.fixture
def pop_template() -> Generator:
    pth = Path(tempfile.gettempdir()) / "Documents" / "datamaps"
    yield pth
    shutil.rmtree(pth)


@pytest.fixture
def master() -> Path:
    return Path.cwd() / "tests" / "resources" / "master.xlsx"


@pytest.fixture
def master_no_col_a() -> Path:
    return Path.cwd() / "tests" / "resources" / "master_empty_col_a.xlsx"


@pytest.fixture()
def master_with_rogue_cell_vals_beyond_col_and_row_range() -> Path:
    return (
        Path.cwd()
        / "tests"
        / "resources"
        / "master_values_beyond_end_of_col_and_row_range.xlsx"
    )


@pytest.fixture
def blank_template() -> Path:
    return Path.cwd() / "tests" / "resources" / "blank_template.xlsm"


@pytest.fixture
def datamap() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/datamap.csv"))


@pytest.fixture
def datamap_reduced() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/datamap_reduced.csv"))


@pytest.fixture
def datamap_csv_unsupported_encodings(request) -> Path:
    here = os.path.abspath(os.curdir)
    return Path(Path(here) / "tests/resources/datamaps_all_encodings" / request.param)


@pytest.fixture
def datamap_csv_supported_encodings(request) -> Path:
    here = os.path.abspath(os.curdir)
    return Path(Path(here) / "tests/resources/datamaps_all_encodings" / request.param)


@pytest.fixture
def datamap_missing_fields() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/datamap_missing_fields.csv"))


@pytest.fixture
def datamap_missing_key_fields() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/datamap_missing_key_fields.csv"))


@pytest.fixture
def datamap_moderately_bad_headers():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_moderately_bad_headers.csv")


@pytest.fixture
def datamap_very_bad_headers():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_very_bad_headers.csv")


@pytest.fixture
def datamap_single_header():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_single_header.csv")


@pytest.fixture
def datamap_no_type_col():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_no_type_col.csv")


@pytest.fixture
def datamap_two_headers():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_two_headers.csv")


@pytest.fixture
def datamap_three_headers():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_three_headers.csv")


@pytest.fixture
def datamap_empty_cols():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_empty_cols.csv")


@pytest.fixture
def datamap_match_test_template():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap_match_test_template.csv")


@pytest.fixture
def blank_org_template():
    return Path(Path.cwd() / "tests/resources/blank_template_password_removed.xlsm")


@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setattr(Config, "PLATFORM_DOCS_DIR", Path("/tmp/Documents/datamaps"))
    monkeypatch.setattr(
        Config, "DATAMAPS_LIBRARY_DATA_DIR", Path("/tmp/.local/share/datamaps-data")
    )
    monkeypatch.setattr(
        Config, "DATAMAPS_LIBRARY_CONFIG_DIR", Path("/tmp/.config/datamaps-data")
    )
    monkeypatch.setattr(
        Config,
        "DATAMAPS_LIBRARY_CONFIG_FILE",
        Path("/tmp/.config/datamaps-data/config.ini"),
    )
    yield Config
    try:
        shutil.rmtree(Config.DATAMAPS_LIBRARY_DATA_DIR)
        shutil.rmtree(Config.DATAMAPS_LIBRARY_CONFIG_DIR)
        shutil.rmtree(Config.PLATFORM_DOCS_DIR)
    except FileNotFoundError:
        pass


@pytest.fixture
def org_test_files_dir():
    return Path.cwd() / "tests" / "resources" / "org_templates"


@pytest.fixture
def template_dict():
    return {
        "filename.xlsm": {
            "data": {
                "To DO": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "To DO",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "To DO",
                        "value": "then update that",
                    },
                },
                "Rich Tea": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "then update that",
                    },
                },
            }
        },
        "filename2.xlsm": {
            "data": {
                "To DO": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "To DO",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "To DO",
                        "value": "then update that",
                    },
                },
                "Rich Tea": {
                    "A1": {
                        "cellref": "A1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "Free text drop down",
                    },
                    "B1": {
                        "cellref": "B1",
                        "data_type": "TEXT",
                        "file_name": "/tmp/Documents/datamaps/input/filename2.xlsm",
                        "sheet_name": "Rich Tea",
                        "value": "then update that",
                    },
                },
            }
        },
    }


@pytest.fixture
def datamap_lst_with_single_sheet():
    return [
        {
            "cellref": "C11",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project/Programme Name",
            "sheet": "Introduction",
        },
        {
            "cellref": "C9",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Department",
            "sheet": "Introduction",
        },
        {
            "cellref": "C10",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Delivery Body",
            "sheet": "Introduction",
        },
        {
            "cellref": "C12",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "TOFGM - TUI ID Number",
            "sheet": "Introduction",
        },
        {
            "cellref": "C13",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Controls Project ID number",
            "sheet": "Introduction",
        },
        {
            "cellref": "C14",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project Type (for TUI use)",
            "sheet": "Introduction",
        },
        {
            "cellref": "C11",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project/Programme Name",
            "sheet": "Introduction",
        },
        {
            "cellref": "C9",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Department",
            "sheet": "Introduction",
        },
        {
            "cellref": "C10",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Delivery Body",
            "sheet": "Introduction",
        },
        {
            "cellref": "C12",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "TOFGM - TUI ID Number",
            "sheet": "Introduction",
        },
        {
            "cellref": "C13",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Controls Project ID number",
            "sheet": "Introduction",
        },
        {
            "cellref": "C14",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project Type (for TUI use)",
            "sheet": "Introduction",
        },
    ]


@pytest.fixture
def datamap_lst_with_sheets_same_as_template_dict():
    return [
        {
            "cellref": "C11",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project/Programme Name",
            "sheet": "To DO",
        },
        {
            "cellref": "C9",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Department",
            "sheet": "To DO",
        },
        {
            "cellref": "C10",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Delivery Body",
            "sheet": "To DO",
        },
        {
            "cellref": "C12",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "TOFGM - TUI ID Number",
            "sheet": "To DO",
        },
        {
            "cellref": "C13",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Controls Project ID number",
            "sheet": "To DO",
        },
        {
            "cellref": "C14",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project Type (for TUI use)",
            "sheet": "To DO",
        },
        {
            "cellref": "C11",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project/Programme Name",
            "sheet": "Rich Tea",
        },
        {
            "cellref": "C9",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Department",
            "sheet": "Rich Tea",
        },
        {
            "cellref": "C10",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Delivery Body",
            "sheet": "Rich Tea",
        },
        {
            "cellref": "C12",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "TOFGM - TUI ID Number",
            "sheet": "Rich Tea",
        },
        {
            "cellref": "C13",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Controls Project ID number",
            "sheet": "Rich Tea",
        },
        {
            "cellref": "C14",
            "data_type": "TEXT",
            "filename": "/tmp/Documents/datamaps/input/dft_datamap.csv",
            "key": "Project Type (for TUI use)",
            "sheet": "Rich Tea",
        },
    ]

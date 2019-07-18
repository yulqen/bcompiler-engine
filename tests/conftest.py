# type: ignore

import os
import shutil
import tempfile
from pathlib import Path

from typing import List, Generator

import pytest

from engine.config import Config
from engine.domain.datamap import DatamapLine
from engine.use_cases.parsing import DatamapLineValueType, TemplateCell


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
        filename=
        "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",  # noqa
    )
    dml2 = DatamapLine(
        key="Department",
        sheet="Introduction",
        cellref="C9",
        data_type="TEXT",
        filename=
        "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",  # noqa  # noqa
    )
    dml3 = DatamapLine(
        key="Delivery Body",
        sheet="Introduction",
        cellref="C10",
        data_type="TEXT",
        filename=
        "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",  # noqa
    )
    dml4 = DatamapLine(
        key="GMPP - IPA ID Number",
        sheet="Introduction",
        cellref="C12",
        data_type="TEXT",
        filename=
        "/home/lemon/code/python/bcompiler-engine/tests/resources/datamap.csv",  # noqa
    )
    return [dml1, dml2, dml3, dml4]


@pytest.fixture
def dat_file() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/extracted_data.dat"))


@pytest.fixture
def spreadsheet_same_data_as_dat_file():
    return Path(Path.cwd() / "tests/resources/test_dat_file_use_case.xlsx")


@pytest.fixture
def resources() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/"))


@pytest.fixture
def doc_directory() -> Generator:
    pth = Path(tempfile.gettempdir()) / "Documents" / "bcompiler"
    yield pth
    shutil.rmtree(pth)


@pytest.fixture
def template() -> Path:
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/test_template.xlsx"))


@pytest.fixture
def datamap() -> str:
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap.csv")


@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setattr(Config, "PLATFORM_DOCS_DIR",
                        Path("/tmp/Documents/bcompiler"))
    yield Config
    try:
        shutil.rmtree(Config.BCOMPILER_LIBRARY_DATA_DIR)
        shutil.rmtree(Config.BCOMPILER_LIBRARY_CONFIG_DIR)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_config_subclassed():
    class TestApplicationConfig(Config):
        "This is created in the application and passed to the library"
        prove = "TestApplicationConfig set"

    yield TestApplicationConfig

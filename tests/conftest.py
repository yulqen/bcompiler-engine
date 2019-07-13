import os
import tempfile
from pathlib import Path

import pytest

from engine.config import Config, init
from engine.domain.datamap import DatamapLine
from engine.use_cases.parsing import DatamapLineValueType, TemplateCell


@pytest.fixture
def template_cell_obj():
    return TemplateCell(
        file_name="test.xlsx",
        sheet_name="Test Sheet 1",
        cell_ref="A10",
        value="Test Value",
        data_type=DatamapLineValueType.TEXT,
    )


@pytest.fixture
def datamapline_list_objects():
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
def resources():
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/"))


@pytest.fixture
def template():
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/test_template.xlsx"))


@pytest.fixture
def datamap():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/datamap.csv")


@pytest.fixture
def mock_config():
    imitation_home = tempfile.gettempdir()
    # we want to call init() here with our mock home directory for testing
    init(imitation_home)
    # likewise, we initialise Config() with our mock home directory
    config = Config(imitation_home)
    yield (imitation_home, config)
    # clean up
    Path.rmdir(Path(imitation_home) / ".bcompiler-engine-data")

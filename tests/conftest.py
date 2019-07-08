import os
import tempfile
from pathlib import Path

import pytest

from engine.config import Config, init


@pytest.fixture
def resources():
    here = os.path.abspath(os.curdir)
    return Path(os.path.join(here, "tests/resources/"))


@pytest.fixture
def template():
    here = os.path.abspath(os.curdir)
    return os.path.join(here, "tests/resources/test_template.xlsx")


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

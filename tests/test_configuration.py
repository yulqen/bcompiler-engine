import tempfile
from pathlib import Path

import pytest

from engine.config import Config, init
"""
Initialising directories and files for use by the application.

We need a data directory in which to store binary, temp and
cache files.
"""


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


def test_set_up_directory(mock_config):
    mock_home = mock_config[0]
    assert Path.exists(Path(mock_home) / ".bcompiler-engine-data")


def test_data_directory_exists(mock_config):
    mock_home = mock_config[0]
    assert mock_config[1].home_dir == Path(mock_home)
    assert mock_config[1].data_dir == Path(
        mock_home) / ".bcompiler-engine-data"

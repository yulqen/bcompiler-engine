import tempfile
from pathlib import Path

import pytest

from engine.config import Config, init
"""
Initialising directories and files for use by the application.

We need a data directory in which to store binary, temp and
cache files.
"""


def test_set_up_directory(mock_config):
    mock_home = mock_config[0]
    assert Path.exists(Path(mock_home) / ".bcompiler-engine-data")


def test_data_directory_exists(mock_config):
    mock_home = mock_config[0]
    assert mock_config[1].home_dir == Path(mock_home)
    assert mock_config[1].data_dir == Path(
        mock_home) / ".bcompiler-engine-data"

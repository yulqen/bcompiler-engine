import platform
import shutil
import tempfile
from pathlib import Path

import pytest

from engine.config import register_config
from engine.exceptions import MissingConfigurationException
"""
Initialising directories and files for use by the application.

We need a data directory in which to store binary, temp and
cache files.
"""


def test_basic_config_variables(mock_config_subclassed):
    if platform.system() == "Linux":
        assert mock_config_subclassed.BCOMPILER_LIBRARY_DATA_DIR == Path(
            Path.home() / ".local/share/bcompiler-data")
        assert mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_DIR == Path(
            Path.home() / ".config/bcompiler")
        assert mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_FILE == Path(
            Path.home() / ".config/bcompiler/config.ini")
    ## TODO write tests for Windows and Mac here

    # Test first that none of these paths exist
    assert not Path(mock_config_subclassed.BCOMPILER_LIBRARY_DATA_DIR).exists()
    assert not Path(
        mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_DIR).exists()
    assert not Path(
        mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_FILE).exists()


def test_required_config_dirs_exist(mock_config_subclassed):
    # Create the required directories and files upon initialisation
    tmp_dir = tempfile.gettempdir()

    if platform.system() == "Linux":
        mock_config_subclassed.BCOMPILER_LIBRARY_DATA_DIR = Path(
            Path(tmp_dir) / "bcompiler-data")
        mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_DIR = Path(
            Path(tmp_dir) / "bcompiler")
        mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_FILE = (
            Path(tmp_dir) /
            mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_DIR / "config.ini")

        ## TODO write tests for Windows and Mac here

        # we call Config.initialise() to set everything up
        mock_config_subclassed.initialise()

        assert mock_config_subclassed.BCOMPILER_LIBRARY_DATA_DIR.exists()
        assert mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_DIR.exists()
        assert mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_FILE.exists()

        # not doing this after yield in confest as we've patch config
        shutil.rmtree(mock_config_subclassed.BCOMPILER_LIBRARY_DATA_DIR)
        shutil.rmtree(mock_config_subclassed.BCOMPILER_LIBRARY_CONFIG_DIR)


def test_library_config_register(mock_config_subclassed):
    # TODO - this needs testing a bit more thoroughly
    register_config(mock_config_subclassed)
    from engine.config import USER_CONFIG

    assert USER_CONFIG == mock_config_subclassed


def test_using_wrong_type_for_config_raises_exception(mock_config_subclassed):
    with pytest.raises(MissingConfigurationException):
        register_config(object)


def test_setting_own_variables_in_config_class(mock_config):
    with pytest.raises(AttributeError):
        prove_var = mock_config.prove

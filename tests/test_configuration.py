import platform
import shutil
from pathlib import Path
"""
Initialising directories and files for use by the application.

We need a data directory in which to store binary, temp and
cache files.
"""


def test_basic_config_variables(mock_config):
    if platform.system() == "Linux":
        assert Path(mock_config.BCOMPILER_LIBRARY_DATA_DIR) == Path(
            Path.home() / ".local/share/bcompiler-data")
        assert Path(mock_config.BCOMPILER_LIBRARY_CONFIG_DIR) == Path(
            Path.home() / ".config/bcompiler-data")
        assert Path(mock_config.BCOMPILER_LIBRARY_CONFIG_FILE) == Path(
            Path.home() / ".config/bcompiler-data/config.ini")
    ## TODO write tests for Windows and Mac here

    # Test first that none of these paths exist
    assert not Path(mock_config.BCOMPILER_LIBRARY_DATA_DIR).exists()
    assert not Path(mock_config.BCOMPILER_LIBRARY_CONFIG_DIR).exists()
    assert not Path(mock_config.BCOMPILER_LIBRARY_CONFIG_FILE).exists()


def test_required_config_dirs_exist(mock_config):
    # Create the required directories and files upon initialisation

    # we call mock_config.initialise() to set everything up
    mock_config.initialise()

    assert Path(mock_config.BCOMPILER_LIBRARY_DATA_DIR).exists()
    assert Path(mock_config.BCOMPILER_LIBRARY_CONFIG_DIR).exists()
    assert Path(mock_config.BCOMPILER_LIBRARY_CONFIG_FILE).exists()


def test_config_values(mock_config):
    mock_config.initialise()
    assert (mock_config.config_parser["PATHS"]["input directory"] ==
            "/home/lemon/Documents/bcompiler/input")
    assert (mock_config.config_parser["PATHS"]["output directory"] ==
            "/home/lemon/Documents/bcompiler/output")
    if platform.system() == "Linux":
        assert (mock_config.config_parser["PATHS"]["document directory"] ==
                "/home/lemon/Documents/bcompiler")

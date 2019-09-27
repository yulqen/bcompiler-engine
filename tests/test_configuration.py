import platform
from pathlib import Path


"""
Initialising directories and files for use by the application.

We need a data directory in which to store binary, temp and
cache files.
"""


def test_basic_config_variables(mock_config):
    if platform.system() == "Linux":
        assert Path(mock_config.DATAMAPS_LIBRARY_DATA_DIR) == Path("/tmp") / Path(
            ".local/share/datamaps-data"
        )
        assert Path(mock_config.DATAMAPS_LIBRARY_CONFIG_DIR) == Path("/tmp") / Path(
            ".config/datamaps-data"
        )
        assert Path(mock_config.DATAMAPS_LIBRARY_CONFIG_FILE) == Path("/tmp") / Path(
            ".config/datamaps-data/config.ini"
        )

    # Test first that none of these paths exist
    assert not Path(mock_config.DATAMAPS_LIBRARY_DATA_DIR).exists()
    assert not Path(mock_config.DATAMAPS_LIBRARY_CONFIG_DIR).exists()
    assert not Path(mock_config.DATAMAPS_LIBRARY_CONFIG_FILE).exists()


def test_required_config_dirs_exist(mock_config):
    # Create the required directories and files upon initialisation

    # we call mock_config.initialise() to set everything up
    mock_config.initialise()

    assert Path(mock_config.DATAMAPS_LIBRARY_DATA_DIR).exists()
    assert Path(mock_config.DATAMAPS_LIBRARY_CONFIG_DIR).exists()
    assert Path(mock_config.DATAMAPS_LIBRARY_CONFIG_FILE).exists()


def test_config_values(mock_config):
    mock_config.initialise()
    USER_NAME = mock_config.USER_NAME
    assert mock_config.config_parser["PATHS"][
        "input directory"
    ] == "/home/{0}/Documents/datamaps/input".format(USER_NAME)
    assert mock_config.config_parser["PATHS"][
        "output directory"
    ] == "/home/{0}/Documents/datamaps/output".format(USER_NAME)
    if platform.system() == "Linux":
        assert mock_config.config_parser["PATHS"][
            "document directory"
        ] == "/home/{0}/Documents/datamaps".format(USER_NAME)

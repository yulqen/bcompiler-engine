from sys import platform
import shutil
from pathlib import Path

from engine.config import check_for_blank, check_for_datamap


"""
Initialising directories and files for use by the application.

We need a data directory in which to store binary, temp and
cache files.
"""


def test_basic_config_variables(mock_config):
    if platform == "Linux":
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
    from sys import platform
    if platform == "linux":
        mock_config.initialise()
        USER_NAME = mock_config.USER_NAME
        assert mock_config.config_parser["PATHS"][
            "input directory"
        ] == "/home/{0}/Documents/datamaps/input".format(USER_NAME)
        assert mock_config.config_parser["PATHS"][
            "output directory"
        ] == "/home/{0}/Documents/datamaps/output".format(USER_NAME)
        assert mock_config.config_parser["PATHS"][
            "document directory"
        ] == "/home/{0}/Documents/datamaps".format(USER_NAME)
    else:
        mock_config.initialise()
        USER_NAME = mock_config.USER_NAME
        assert mock_config.config_parser["PATHS"][
                   "input directory"
               ] == "C:\\Users\\{0}\\Documents\\datamaps\\input".format(USER_NAME)
        assert mock_config.config_parser["PATHS"][
                   "output directory"
               ] == "C:\\Users\\{0}\\Documents\\datamaps\\output".format(USER_NAME)
        assert mock_config.config_parser["PATHS"][
                   "document directory"
               ] == "C:\\Users\\{0}\\Documents\\datamaps".format(USER_NAME)



def test_presence_of_aux_files(mock_config, blank_template, datamap):
    """Tests that aux files are in place.

    Checks that a blank template and datamap is there.
    """
    mock_config.initialise()
    shutil.copy2(blank_template, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    shutil.copy2(datamap, (Path(mock_config.PLATFORM_DOCS_DIR) / "input"))
    blank_t = check_for_blank(mock_config)
    dm_t = check_for_datamap(mock_config)
    assert blank_t[0]
    assert blank_t[1] == "blank_template.xlsm"
    assert dm_t[0]
    assert dm_t[1] == "datamap.csv"


def test_lack_of_aux_files(mock_config):
    """Tests that aux files are in place.

    Checks that a blank template and datamap is there.
    """
    mock_config.initialise()
    blank_t = check_for_blank(mock_config)
    dm_t = check_for_datamap(mock_config)
    assert not blank_t[0]
    assert blank_t[1] == ""
    assert not dm_t[0]
    assert dm_t[1] == ""

import getpass
import logging
import os
import platform
import textwrap
from configparser import ConfigParser
from pathlib import Path
from typing import Tuple

from appdirs import user_config_dir, user_data_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)


def _platform_docs_dir() -> Path:
    if platform.system() == "Linux":
        return Path.home() / "Documents" / "datamaps"
    if platform.system() == "Darwin":
        return Path.home() / "Documents" / "datamaps"
    else:
        return Path.home() / "Documents" / "datamaps"


class Config:
    "This is created in the application and passed to the library."

    # Specifically for Github Actions CI
    USER_NAME = (
        os.environ["GITHUB_ACTIONS_RUNNER"]
        if os.environ.get("GITHUB_ACTIONS_RUNNER")
        else getpass.getuser()
    )

    DATAMAPS_LIBRARY_DATA_DIR = user_data_dir("datamaps-data", USER_NAME)
    DATAMAPS_LIBRARY_CONFIG_DIR = user_config_dir("datamaps-data", USER_NAME)
    DATAMAPS_LIBRARY_CONFIG_FILE = os.path.join(
        DATAMAPS_LIBRARY_CONFIG_DIR, "config.ini"
    )
    PLATFORM_DOCS_DIR = _platform_docs_dir()
    FULL_PATH_INPUT = Path(PLATFORM_DOCS_DIR) / "input"
    FULL_PATH_OUTPUT = Path(PLATFORM_DOCS_DIR) / "output"
    ACCEPTABLE_VALIDATION_TYPES = ["TEXT", "NUMBER", "DATE"]
    TEMPLATE_ROW_LIMIT = 500
    config_parser = ConfigParser()
    base_config = textwrap.dedent(
        """\
    [DEFAULT]
    # This is the value that appears in cell A1 in a master
    # Might be more relevant to rename it to project name, for example
    return reference name = file name
    master file name = master.xlsx
    datamap file name = datamap.csv
    blank file name = blank_template.xlsm

    TEMPLATE_ROW_LIMIT = 500

    [PATHS]
    document directory = {0}
    input directory = {1}
    output directory = {2}

    """
    ).format(PLATFORM_DOCS_DIR, FULL_PATH_INPUT, FULL_PATH_OUTPUT)

    @classmethod
    def initialise(cls) -> None:
        if not Path(cls.DATAMAPS_LIBRARY_DATA_DIR).exists():
            logger.info(f"Creating data directory at {cls.DATAMAPS_LIBRARY_DATA_DIR}.")
            Path(cls.DATAMAPS_LIBRARY_DATA_DIR).mkdir(parents=True)
        if not Path(cls.DATAMAPS_LIBRARY_CONFIG_DIR).exists():
            logger.info(
                f"Creating config directory at {cls.DATAMAPS_LIBRARY_CONFIG_DIR}."
            )
            Path(cls.DATAMAPS_LIBRARY_CONFIG_DIR).mkdir(parents=True)
        if not Path(cls.DATAMAPS_LIBRARY_CONFIG_FILE).exists():
            # logger.info(f"Creating config file at {cls.DATAMAPS_LIBRARY_CONFIG_FILE}.")
            Path(cls.DATAMAPS_LIBRARY_CONFIG_FILE).write_text(cls.base_config)

        cls.config_parser.read(cls.DATAMAPS_LIBRARY_CONFIG_FILE)

        # then we need to create the docs directory if it doesn't exist
        try:
            input_dir = Path(cls.PLATFORM_DOCS_DIR / "input")  # type: ignore
        except TypeError:
            raise TypeError("Unable to detect operating system")
        try:
            output_dir = Path(cls.PLATFORM_DOCS_DIR / "output")  # type: ignore
        except TypeError:
            raise TypeError("Unable to detect operating system")
        if not input_dir.exists():
            logger.warning("Default input directory does not exist.")
            logger.info("Creating input directory.")
            input_dir.mkdir(parents=True)
        if not output_dir.exists():
            logger.warning("Required output directory does not exist.")
            logger.info("Creating output directory.")
            output_dir.mkdir(parents=True)


def check_for_blank(config: Config) -> Tuple[bool, str]:
    """Checks for a blank template, named appropriately, in the Documents/input directory.

    Config should be initialised before passing to this function.
    """
    blank = (
        config.PLATFORM_DOCS_DIR
        / "input"
        / config.config_parser["DEFAULT"]["blank file name"]
    )
    if blank.exists():
        return (True, blank.name)
    else:
        return (False, "")


def check_for_datamap(config: Config) -> Tuple[bool, str]:
    """Checks for a datamap file, named appropriately, in the Documents/input directory.

    Config should be initialised before passing to this function.
    """
    dm = (
        config.PLATFORM_DOCS_DIR
        / "input"
        / config.config_parser["DEFAULT"]["datamap file name"]
    )
    if dm.exists():
        return (True, dm.name)
    else:
        return (False, "")


def delete_config_file(config: Config) -> None:
    """Deletes the configuration file - config.ini."""
    try:
        os.remove(config.DATAMAPS_LIBRARY_CONFIG_FILE)
        logger.info(
            "Configuration reset to default. The necessary configuration files will be recreated on next execution of any datamaps command."
        )
    except FileNotFoundError:
        raise


def show_config_file(config: Config) -> None:
    """
    Shows the path of the configuration file, config.ini.
    """
    logger.info(f"The configuration file is at {config.DATAMAPS_LIBRARY_CONFIG_FILE}")

import os
import platform
import textwrap
from configparser import ConfigParser
from pathlib import Path

from appdirs import user_config_dir, user_data_dir


def _platform_docs_dir() -> Path:
    if platform.system() == "Linux":
        return Path.home() / "Documents" / "bcompiler"
    if platform.system() == "Darwin":
        return Path.home() / "Documents" / "bcompiler"
    else:
        return Path.home() / "Documents" / "bcompiler"


class Config:
    "This is created in the application and passed to the library."

    USER_NAME = os.getlogin()
    BCOMPILER_LIBRARY_DATA_DIR = user_data_dir("bcompiler-data", USER_NAME)
    BCOMPILER_LIBRARY_CONFIG_DIR = user_config_dir("bcompiler-data", USER_NAME)
    BCOMPILER_LIBRARY_CONFIG_FILE = os.path.join(
        BCOMPILER_LIBRARY_CONFIG_DIR, "config.ini"
    )
    PLATFORM_DOCS_DIR = _platform_docs_dir()
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

    [PATHS]
    document directory = {0}
    input directory = %(document directory)s/input
    output directory =%(document directory)s/output

    """
    ).format(PLATFORM_DOCS_DIR)

    @classmethod
    def initialise(cls) -> None:
        if not Path(cls.BCOMPILER_LIBRARY_DATA_DIR).exists():
            Path(cls.BCOMPILER_LIBRARY_DATA_DIR).mkdir(parents=True)
        if not Path(cls.BCOMPILER_LIBRARY_CONFIG_DIR).exists():
            Path(cls.BCOMPILER_LIBRARY_CONFIG_DIR).mkdir(parents=True)
        if not Path(cls.BCOMPILER_LIBRARY_CONFIG_FILE).exists():
            Path(cls.BCOMPILER_LIBRARY_CONFIG_FILE).write_text(cls.base_config)
        cls.config_parser.read(cls.BCOMPILER_LIBRARY_CONFIG_FILE)


        # writing the config file again to accommodate changes
        # TODO fix permissions bug in Windows when doing this
        Path(cls.BCOMPILER_LIBRARY_CONFIG_FILE).write_text(cls.base_config)
        cls.config_parser.read(cls.BCOMPILER_LIBRARY_CONFIG_FILE)

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
            input_dir.mkdir(parents=True)
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

# config.py
"""
######################################################
#CONFIG MUST BE PROVIDED BY THE FRONT-END APPLICATION#
######################################################

Configuration and application file system locations:

This should all be in the CLI application - not the library.
We need an interface in the library which expects these variables.

Linux
-----

configuration:              ~/.config/bcompiler-engine/config.ini
cache/serialized data:      ~/.bcompiler-engine-data
document drop directory:    AS PER CONFIG.INI
                            AS PER CONFIG.INI

Mac
---

configuration:              ~/Library/Application Support/bcompiler-engine/config.ini
cache/serialized data:      ~/.bcompiler-engine-data
document drop directory:    AS PER CONFIG.INI
                            AS PER CONFIG.INI

Windows
-------

configuration:              ~/Library/Application Support/bcompiler-engine/config.ini
cache/serialized data:      ~/.bcompiler-engine-data
document drop directory:    AS PER CONFIG.INI
                            AS PER CONFIG.INI

"""

import os
import shutil
import sys
import textwrap
from configparser import ConfigParser
from pathlib import Path

import appdirs


class Config:
    "This is created in the application and passed to the library."

    USER_NAME = os.getlogin()

    BCOMPILER_LIBRARY_DATA_DIR = appdirs.user_data_dir("bcompiler-data",
                                                       USER_NAME)
    BCOMPILER_LIBRARY_CONFIG_DIR = appdirs.user_config_dir(
        "bcompiler-data", USER_NAME)
    BCOMPILER_LIBRARY_CONFIG_FILE = os.path.join(BCOMPILER_LIBRARY_CONFIG_DIR,
                                                 "config.ini")
    config_parser = ConfigParser()

    base_config = textwrap.dedent("""\
    [PATHS]
    import directory = /home/lemon/Documents/bcompiler/import
    """)

    @classmethod
    def initialise(cls):
        if not Path(cls.BCOMPILER_LIBRARY_DATA_DIR).exists():
            Path(cls.BCOMPILER_LIBRARY_DATA_DIR).mkdir()
        if not Path(cls.BCOMPILER_LIBRARY_CONFIG_DIR).exists():
            Path(cls.BCOMPILER_LIBRARY_CONFIG_DIR).mkdir()
        if not Path(cls.BCOMPILER_LIBRARY_CONFIG_FILE).exists():
            Path(cls.BCOMPILER_LIBRARY_CONFIG_FILE).write_text(cls.base_config)
            cls.config_parser.read(cls.BCOMPILER_LIBRARY_CONFIG_FILE)

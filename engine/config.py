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

from configparser import ConfigParser
from pathlib import Path


class Config:

    "Interact with config variables."

    config_parser = ConfigParser()
    config_file_path = Path.home() / ".bcompiler-engine-data" / "config.ini"

    def __init__(self, home_dir=False):
        if not home_dir:
            self.home_dir = Path.home()
        else:
            self.home_dir = Path(home_dir)
        self._set_data_dir()

    def _set_data_dir(self):
        if Path(self.home_dir / ".bcompiler-engine-data").exists():
            self.data_dir = self.home_dir / ".bcompiler-engine-data"
        else:
            self.data_dir = Path.mkdir(self.home_dir /
                                       ".bcompiler-engine-data")


def init(home_dir: str = None):
    """
    If passed no arguments, will create a directory called
    .bcompiler-engine-data in the user's home directory if
    it is not already there.
    """
    if home_dir:
        if Path.exists(Path(home_dir) / ".bcompiler-engine-data"):
            print("Set up .bcompiler-engine-data")
            return
        else:
            Path.mkdir(Path(home_dir) / ".bcompiler-engine-data")
    else:
        if Path.exists(Path.home() / ".bcompiler-engine-data"):
            return
        else:
            Path.mkdir(Path.home() / ".bcompiler-engine-data")
            print("Set up .bcompiler-engine-data")

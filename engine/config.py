# config.py

from pathlib import Path


def init(home_dir: str = False):
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


class Config:
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

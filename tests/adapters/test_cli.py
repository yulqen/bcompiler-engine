from engine.adapters.cli import import_and_create_master
from engine.config import Config


def test_create_master_in_memory():
    Config.initialise()
    import_and_create_master()

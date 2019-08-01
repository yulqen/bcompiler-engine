import pytest

from engine.adapters.cli import import_and_create_master
from engine.config import Config


@pytest.mark.skip("Do not run this in the suite - it does not use test config")
def test_create_master_in_memory():
    Config.initialise()
    import_and_create_master()

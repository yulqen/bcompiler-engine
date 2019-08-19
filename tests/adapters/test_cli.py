import pytest

from engine.adapters.cli import (import_and_create_master,
                                 write_master_to_templates)
from engine.config import Config


@pytest.mark.skip("Do not run this in the suite - it does not use test config")
def test_create_master_in_memory():
    Config.initialise()
    import_and_create_master()


@pytest.mark.skip("Do not run this in the suite - it does not use test config")
def test_populate_blanks_from_master(mock_config, blank_template, datamap, master):
    Config.initialise()
    breakpoint()
    write_master_to_templates(datamap, blank_template, master)

# cli adapters
from pathlib import Path

import engine.use_cases.parsing
from engine.config import Config
from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.repository.master import MasterOutputRepository
from engine.repository.templates import InMemoryPopulatedTemplatesRepository
from engine.use_cases.parsing import CreateMasterUseCase


def import_and_create_master(echo_funcs):
    """Import all spreadsheet files from input directory and process with datamap.

    echo_func - a function sent from the front-end interface allowing for suitable output (stdout, etc)
    echo_func_params - parameters to be used with echo_func

    Create master spreadsheet immediately.
    """

    #patch ECHO_FUNC for datamap creation - hack!
    setattr(engine.use_cases.parsing, "ECHO_FUNC_GREEN", echo_funcs["click_echo_green"])
    setattr(engine.use_cases.parsing, "ECHO_FUNC_RED", echo_funcs["click_echo_red"])
    setattr(engine.use_cases.parsing, "ECHO_FUNC_YELLOW", echo_funcs["click_echo_yellow"])
    setattr(engine.use_cases.parsing, "ECHO_FUNC_WHITE", echo_funcs["click_echo_white"])


    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        Config.PLATFORM_DOCS_DIR / "input"
    )
    master_fn = Config.config_parser["DEFAULT"]["master file name"]
    dm_fn = Config.config_parser["DEFAULT"]["datamap file name"]
    dm = Path(tmpl_repo.directory_path) / dm_fn
    dm_repo = InMemorySingleDatamapRepository(str(dm))
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCase(dm_repo, tmpl_repo, output_repo)
    uc.execute(master_fn)
    echo_funcs["click_echo_green"]("{} successfully created in {}\n".format(master_fn, Path(Config.PLATFORM_DOCS_DIR / "output")))

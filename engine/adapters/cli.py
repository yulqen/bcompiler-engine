# cli adapters
import logging
import sys
from pathlib import Path
from typing import List

from openpyxl import load_workbook

import engine.use_cases.parsing
from engine.config import (
    Config,
    check_for_blank,
    check_for_datamap,
    delete_config_file,
    show_config_file,
)
from engine.exceptions import DatamapNotCSVException
from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.repository.master import MasterOutputRepository, ValidationOnlyRepository
from engine.repository.templates import (
    InMemoryPopulatedTemplatesRepository,
    MultipleTemplatesWriteRepo,
)
from engine.use_cases.output import WriteMasterToTemplates
from engine.use_cases.parsing import (
    CreateMasterUseCase,
    CreateMasterUseCaseWithValidation,
)
from engine.utils.extraction import data_validation_report, datamap_reader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)


def check_aux_files(config: Config):
    """Check the presence of the blank template, the datamap and the validity of the datmap"""
    blank_t = check_for_blank(config)
    if blank_t[0]:
        logger.info(f"Blank template named {blank_t[1]} present in input directory.")
    else:
        logger.critical(
            f"No blank template present. Config requires a file called "
            f"{config.config_parser['DEFAULT']['blank file name']} in input directory."
        )
        sys.exit(0)
    dm_t = check_for_datamap(config)
    if dm_t[0]:
        logger.info(f"Datamap file named {dm_t[1]} present in input directory.")
    else:
        logger.critical(
            f"No datamap file present. Config requires a file called "
            f"{config.config_parser['DEFAULT']['datamap file name']} in input directory."
        )
        sys.exit(0)
    # if we get this far, there is a datamap file, so we can run this
    dm_name = config.config_parser["DEFAULT"]["datamap file name"]
    if datamap_reader(config.PLATFORM_DOCS_DIR / "input" / dm_name):
        logger.info(
            "Datamap file passes tests. Check any WARNING messages. Ok to proceed."
        )
    else:
        logger.critical("Datamap tests failed")


def report_data_validations_in_file(file: Path) -> List[str]:
    """Take a file and report details of data validations.

    :param file:
    :type Path:
    """
    try:
        wb = load_workbook(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Cannot find {file}")
    output = []
    sheets = wb.get_sheet_names()
    for s in sheets:
        ws = wb[s]
        report = data_validation_report(ws)
        for x in [r.report_line for r in report]:
            output.append(x)
    return output


def write_master_to_templates(
    blank_template: Path, datamap: Path, master: Path
) -> None:
    output_repo = MultipleTemplatesWriteRepo(blank_template)
    uc = WriteMasterToTemplates(output_repo, datamap, master, blank_template)
    uc.execute()


def import_and_create_master(echo_funcs, datamap=None, **kwargs):
    """Import all spreadsheet files from input directory and process with datamap.

    echo_func - a function sent from the front-end interface allowing for suitable output (stdout, etc)
    echo_func_params - parameters to be used with echo_func

    Create master spreadsheet immediately.
    """
    # patch ECHO_FUNC for datamap creation - hack!
    setattr(engine.use_cases.parsing, "ECHO_FUNC_GREEN", echo_funcs["click_echo_green"])
    setattr(engine.use_cases.parsing, "ECHO_FUNC_RED", echo_funcs["click_echo_red"])
    setattr(
        engine.use_cases.parsing, "ECHO_FUNC_YELLOW", echo_funcs["click_echo_yellow"]
    )
    setattr(engine.use_cases.parsing, "ECHO_FUNC_WHITE", echo_funcs["click_echo_white"])

    master_fn = Config.config_parser["DEFAULT"]["master file name"]
    if kwargs.get("rowlimit"):
        Config.TEMPLATE_ROW_LIMIT = kwargs.get("rowlimit")

    if kwargs.get("inputdir"):
        inputdir = kwargs.get("inputdir")
    else:
        inputdir = Config.PLATFORM_DOCS_DIR / "input"
    if kwargs.get("validationonly"):
        output_repo = ValidationOnlyRepository
        master_fn = ""
    else:
        output_repo = MasterOutputRepository

    if Config.TEMPLATE_ROW_LIMIT < 50:
        logger.warning(
            f"Row limit is set to {Config.TEMPLATE_ROW_LIMIT} (default is 500). This may be unintentionally low. Check datamaps import templates --help"
        )
    else:
        logger.info(f"Row limit is set to {Config.TEMPLATE_ROW_LIMIT}.")

    tmpl_repo = InMemoryPopulatedTemplatesRepository(inputdir)
    if datamap:
        dm_fn = datamap
    else:
        dm_fn = Config.config_parser["DEFAULT"]["datamap file name"]
    dm = Path(tmpl_repo.directory_path) / dm_fn
    dm_repo = InMemorySingleDatamapRepository(dm)
    if dm_repo.is_typed:
        uc = CreateMasterUseCaseWithValidation(dm_repo, tmpl_repo, output_repo)
    else:
        if output_repo == ValidationOnlyRepository:
            logger.critical(
                "Cannot validate data. The datamap needs to have a 'type' column."
            )
            sys.exit(1)
        uc = CreateMasterUseCase(dm_repo, tmpl_repo, output_repo)
    try:
        uc.execute(master_fn)
    except FileNotFoundError as e:
        raise FileNotFoundError(e)
    except DatamapNotCSVException:
        raise


def delete_config(config) -> None:
    try:
        delete_config_file(config)
    except FileNotFoundError:
        logger.critical(
            f"Could not find {config.DATAMAPS_LIBRARY_CONFIG_FILE}. Run datamaps config restart to recreate it and reset defaults."
        )


def show_config(config) -> None:
    show_config_file(config)

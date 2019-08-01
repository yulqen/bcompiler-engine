# cli adapters
from pathlib import Path

from engine.repository.templates import InMemoryPopulatedTemplatesRepository
from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.repository.master import MasterOutputRepository
from engine.use_cases.parsing import CreateMasterUseCase
from engine.config import Config


def import_and_create_master():
    """Import all spreadsheet files from input directory and process with datamap.

    Create master spreadsheet immediately.
    """
    tmpl_repo = InMemoryPopulatedTemplatesRepository(
        Config.PLATFORM_DOCS_DIR / "input"
    )
    # TODO make the name configurable in config.ini
    dm = Path(tmpl_repo.directory_path) / "datamap.csv"
    dm_repo = InMemorySingleDatamapRepository(str(dm))
    output_repo = MasterOutputRepository
    uc = CreateMasterUseCase(dm_repo, tmpl_repo, output_repo)
    uc.execute("master.xlsx")

"""
Use cases related to writing data to an output repository.
"""

from pathlib import Path
from typing import List, Tuple

from openpyxl import load_workbook

from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.use_cases.parsing import ParseDatamapUseCase


class WriteMasterToTemplates:
    def __init__(self, output_repo, datamap: Path, master: Path, blank_template: Path):
        self.datamap = datamap
        self.master_path = master
        self.master_sheet = load_workbook(master).active
        self.blank_template = blank_template
        self.key_cell_ref_pairs: List[Tuple[str, str]]

    def _check_datamap_matches_cola(self) -> bool:
        parsed_dm_data = self._parse_dm_uc.execute(obj=True)
        self.key_cell_ref_pairs = [(x.key, x.cellref) for x in parsed_dm_data]
        # master should have only one sheet
        # miss out A1
        _col_a_vals = [x.value.strip() for x in next(self.master_sheet.columns)][1:]
        _pass = zip([x[0] for x in self.key_cell_ref_pairs], _col_a_vals)
        return all([x[0] == x[1] for x in _pass])

    def execute(self) -> None:
        """
        Writes a master file to multiple templates using blank_template,
        based on the blank_template and the datamap
        """
        breakpoint()
        self.parse_dm_repo = InMemorySingleDatamapRepository(self.datamap)
        self._parse_dm_uc = ParseDatamapUseCase(self.parse_dm_repo)
        assert self._check_datamap_matches_cola()

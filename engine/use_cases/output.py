"""
Use cases related to writing data to an output repository.
"""

import logging
from pathlib import Path
from typing import List, NamedTuple

from openpyxl import load_workbook

from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.use_cases.parsing import ParseDatamapUseCase

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


class ColData(NamedTuple):
    key: str
    sheet: str
    cellref: str
    value: str
    file_name: str


MASTER_COL_DATA = List[ColData]
MASTER_DATA_FOR_FILE = List[MASTER_COL_DATA]


class WriteMasterToTemplates:
    def __init__(self, output_repo, datamap: Path, master: Path, blank_template: Path):
        self.output_repo = output_repo
        self._datamap = datamap
        self._master_path = master
        # Review whether this is a good idea:
        #   It should be ok because of the relative simplicity of master.xlsx files
        self._master_sheet = load_workbook(master).active
        self._blank_template = blank_template
        self._col_a_vals: List[str]

    def _check_datamap_matches_cola(self) -> bool:
        parsed_dm_data = self._parse_dm_uc.execute(obj=True)
        self._dml_line_tup = [(x.key, x.sheet, x.cellref) for x in parsed_dm_data]
        self._col_a_vals = [x.value.strip() for x in next(self._master_sheet.columns)][
            1:
        ]
        _pass = zip([x[0] for x in self._dml_line_tup], self._col_a_vals)
        return all([x[0] == x[1] for x in _pass])

    def _get_keys_in_datamap_not_in_master(self) -> List[str]:
        dm_keys_s = set([x[0] for x in self._dml_line_tup])
        master_keys_s = set(self._col_a_vals)
        return list(dm_keys_s - master_keys_s)

    def execute(self) -> None:
        """
        Writes a master file to multiple templates using blank_template,
        based on the blank_template and the datamap.
        """

        master_data: MASTER_DATA_FOR_FILE = []

        self.parse_dm_repo = InMemorySingleDatamapRepository(str(self._datamap))
        self._parse_dm_uc = ParseDatamapUseCase(self.parse_dm_repo)
        if not self._check_datamap_matches_cola():
            _missing_keys = self._get_keys_in_datamap_not_in_master()
            # You shall not pass if this is a problem
            raise RuntimeError(
                "The following keys are in the datamap "
                "but not in the master: {}. Not continuing".format(
                    [x for x in _missing_keys]
                )
            )
        for col in list(self._master_sheet.columns)[1:]:
            file_name = col[0].value.split(".")[0]
            x = zip(self._dml_line_tup, col[1:])
            tups: MASTER_COL_DATA = [ColData(key=item[0][0], sheet=item[0][1], cellref=item[0][2], value=item[1].value, file_name=file_name) for item in x]
            master_data.append(tups)

        self.output_repo.write(master_data, file_name, from_json=False)

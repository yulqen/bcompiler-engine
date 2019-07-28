# repository/master.py
from pathlib import Path

from openpyxl import Workbook

from engine.config import Config


class MasterOutputRepository:
    def __init__(self, data, output_file_name):
        self.data = data
        self.output_filename = output_file_name

    def save(self):
        # TODO - this is hard-coding the first two cols, where we need to keys as Col 1
        output_path = Path(Config.PLATFORM_DOCS_DIR) / "output"
        wb = Workbook()
        ws = wb.active
        ws.title = "Master"
        _get_first = self.data[0]
        _file_name = list(_get_first.keys())[0][0].split(".")[0]
        ws.cell(column=1, row=1, value="file name")
        ws.cell(column=2, row=1, value=_file_name)
        for idx, row_data in enumerate(self.data, start=2):
            key = list(row_data.keys())[0][1]
            val = row_data[list(row_data.keys())[0]]
            ws.cell(column=1, row=idx, value=key)
            ws.cell(column=2, row=idx, value=val)
        wb.save(output_path / self.output_filename)

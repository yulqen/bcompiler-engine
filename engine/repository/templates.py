import json
from pathlib import Path

from ..serializers.template import ParsedTemplatesSerializer
from ..use_cases.parsing import parse_multiple_xlsx_files
from ..utils.extraction import get_xlsx_files


class InMemoryPopulatedTemplatesRepository:
    def __init__(self, directory_path: Path):
        self.directory_path = directory_path

    def list_as_json(self):
        "Return data from a directory of populated templates as json."
        excel_files = get_xlsx_files(self.directory_path)
        data = parse_multiple_xlsx_files(excel_files)
        return json.dumps(data)

# engine.reports.validation.py
#
# Write a validation report to a CSV file.

import csv
from dataclasses import dataclass
from typing import List

from engine.config import Config


@dataclass
class ValidationCheck:
    passes: bool
    filename: str
    key: str
    value: str
    cellref: str
    sheetname: str
    wanted: str
    got: str


pass_str = {"True": "PASS", "False": "FAIL"}


class ValidationReportCSV:
    """
    Writes a CSV output for validation_data at
    Config.FULL_PATH_OUTPUT/validation_report.csv
    """

    def __init__(self, validation_data: List[ValidationCheck]):
        self.data = validation_data

    def write(self) -> None:
        with open(
            Config.FULL_PATH_OUTPUT / "validation_report.csv", "w", newline=""
        ) as csvfile:
            fieldnames = [
                "Pass Status",
                "Filename",
                "Key",
                "Value",
                "Cell Reference",
                "Sheet Name",
                "Expected Type",
                "Got Type",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.data:
                writer.writerow(
                    {
                        "Pass Status": pass_str[str(item.passes)],
                        "Filename": item.filename,
                        "Key": item.key,
                        "Value": item.value,
                        "Cell Reference": item.cellref,
                        "Sheet Name": item.sheetname,
                        "Expected Type": item.wanted,
                        "Got Type": item.got,
                    }
                )

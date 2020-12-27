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
    value: str
    cellref: str
    sheetname: str
    wanted: str
    got: str


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
                "Filename",
                "Value",
                "Cell Reference",
                "Expected Type",
                "Got Type",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.data:
                writer.writerow(
                    {
                        "Filename": item.filename,
                        "Value": item.value,
                        "Cell Reference": item.cellref,
                        "Expected Type": item.wanted,
                        "Got Type": item.got,
                    }
                )

import fnmatch
import hashlib
import os
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, List

from engine.domain.template import TemplateCell


def _get_xlsx_files(directory: str) -> List[Path]:
    "Return a list of Path objects for each xlsx file in directory, or raise an exception."
    output = []
    if not os.path.isabs(directory):
        raise RuntimeError("Require absolute path here")
    for file_path in os.listdir(directory):
        if fnmatch.fnmatch(file_path, "*.xls[xm]"):
            output.append(Path(os.path.join(directory, file_path)))
    return output


def _get_cell_data(filepath: Path, data: Dict[Any, Any], sheet_name: str,
                   cellref: str) -> Dict[str, str]:
    """Given a Path and a dict of data - and a sheet name, AND a cellref..

    Return:
        - a dict representing the TemplateCell in string format
    """
    _file_data = data[filepath.name]["data"]
    return _file_data[sheet_name][cellref]


def _clean(target_str: str, is_cellref: bool = False) -> str:
    "Rids a string of its most common problems: spacing, capitalisation,etc."
    if not isinstance(target_str, str):
        raise TypeError("Can only clean a string.")
    output_str = target_str.lstrip().rstrip()
    if is_cellref:
        output_str = output_str.upper()
    return output_str


def _extract_sheets(lst_of_tcs: List[TemplateCell]
                    ) -> Dict[str, List[TemplateCell]]:
    "Given a list of TemplateCell objects, returns the list but as a dict sorted by its sheet_name"
    output: Dict[str, List[TemplateCell]] = {}
    data = sorted(lst_of_tcs, key=lambda x: x.sheet_name)
    for k, group in groupby(data, key=lambda x: x.sheet_name):
        output.update({k: list(group)})
    return output


def _extract_cellrefs(lst_of_tcs) -> Dict[str, dict]:
    """Extract value from TemplateCell.cellref for each TemplateCell in a list to group them.

    When given a list of TemplateCell objects, this function extracts each TemplateCell
    by it's cellref value and groups them according. In the curent implementation, this is
    only called on a list of TemplateCell objects which have the same sheet_name value, and
    therefore expects to find only a single cellref value each time, meaning that the list
    produced by groupby() can be removed and the single value return. Returns an exception
    if this list has more than one object.

    Args:
        lst_of_tcs: List of TemplateCell objects.

    Raises:
        RuntimeError: if more than one cellref value is found in the list.

    Returns:
        Dictionary whose key is the cellref and value is the TemplateCell that contains it.

    """
    output: Dict[str, dict] = {}
    data = sorted(lst_of_tcs, key=lambda x: x["cellref"])
    for k, group in groupby(data, key=lambda x: x["cellref"]):
        result = list(group)
        if len(result) > 1:
            raise RuntimeError(
                f"Found duplicate sheet/cellref item when extracting keys.")
        result = result[0]
        output.update({k: result})
    return output


def _hash_single_file(filepath: Path) -> str:
    "Return a checksum for a given file at Path"
    if not filepath.is_file():
        raise RuntimeError(f"Cannot checksum {filepath}")
    hash_obj = hashlib.md5(open(filepath, "rb").read())
    return hash_obj.digest().hex()


def _hash_target_files(list_of_files: List[Path]) -> Dict[str, str]:
    """Hash each file in list_of_files.

    Given a list of files, return a dict containing the file name as
    keys and md5 hash as value for each file.
    """
    output = {}
    for file_name in list_of_files:
        if os.path.isfile(file_name):
            hash_obj = hashlib.md5(open(file_name, "rb").read())
            output.update({file_name.name: hash_obj.digest().hex()})
    return output

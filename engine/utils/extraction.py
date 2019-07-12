import fnmatch
import hashlib
import os
from itertools import groupby
from pathlib import Path
from typing import Dict, List, Optional

from engine.domain.template import TemplateCell


def get_xlsx_files(directory: Path) -> List[Path]:
    """
    Return a list of Path objects for each xlsx file in directory,
    or raise an exception.
    """
    output = []
    if not os.path.isabs(directory):
        raise RuntimeError("Require absolute path here")
    for file_path in os.listdir(directory):
        if fnmatch.fnmatch(file_path, "*.xls[xm]"):
            output.append(Path(os.path.join(directory, file_path)))
    return output


def get_cell_data(filepath: Path, data: List[TemplateCell], sheet_name: str,
                  cell_ref: str) -> Optional[TemplateCell]:
    """
    Given a list of TemplateCell items, a sheet name and a cell reference,
    return a single TemplateCell object.
    """
    _file_data = data[filepath.name]["data"]
    return _file_data[sheet_name][cell_ref]


def clean(target_str: str, is_cell_ref: bool = False):
    """
    Rids a string of its most common problems: spacing, capitalisation,etc.
    """
    if not isinstance(target_str, str):
        raise TypeError("Can only clean a string.")
    output_str = target_str.lstrip().rstrip()
    if is_cell_ref:
        output_str = output_str.upper()
    return output_str


def _extract_sheets(lst_of_tcs: List[TemplateCell]
                    ) -> Dict[str, List[TemplateCell]]:
    output: Dict[str, List[TemplateCell]] = {}
    data = sorted(lst_of_tcs, key=lambda x: x.sheet_name)
    for k, g in groupby(data, key=lambda x: x.sheet_name):
        output.update({k: list(g)})
    return output


def _extract_cellrefs(lst_of_tcs: List[TemplateCell]
                      ) -> Dict[str, TemplateCell]:
    """Extract value from TemplateCell.cell_ref for each TemplateCell in a list to group them.

    When given a list of TemplateCell objects, this function extracts each TemplateCell
    by it's cell_ref value and groups them according. In the curent implementation, this is
    only called on a list of TemplateCell objects which have the same sheet_name value, and
    therefore expects to find only a single cell_ref value each time, meaning that the list
    produced by groupby() can be removed and the single value return. Returns an exception
    if this list has more than one object.

    Args:
        lst_of_tcs: List of TemplateCell objects.

    Raises:
        RuntimeError: if more than one cell_ref value is found in the list.

    Returns:
        Dictionary whose key is the cell_ref and value is the TemplateCell that contains it.

    """

    output: Dict[str, TemplateCell] = {}
    data = sorted(lst_of_tcs, key=lambda x: x.cell_ref)
    for k, g in groupby(data, key=lambda x: x.cell_ref):
        result = list(g)
        if len(result) > 1:
            raise RuntimeError(
                f"Found duplicate sheet/cell_ref item when extracting keys.")
        else:
            result = result[0]
            output.update({k: result})
    return output


def hash_single_file(filepath: Path) -> bytes:
    if not filepath.is_file():
        raise RuntimeError(f"Cannot checksum {filepath}")
    else:
        hash_obj = hashlib.md5(open(filepath, "rb").read())
        return hash_obj.digest()


def hash_target_files(list_of_files: List[Path]) -> Dict[str, bytes]:
    """Hash each file in list_of_files.

    Given a list of files, return a dict containing the file name as
    keys and md5 hash as value for each file.
    """
    output = {}
    for file_name in list_of_files:
        if os.path.isfile(file_name):
            hash_obj = hashlib.md5(open(file_name, "rb").read())
            output.update({file_name.name: hash_obj.digest()})
    return output

import hashlib
import logging
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Union
from zipfile import BadZipFile

from lxml import etree
from lxml.etree import Element

from engine.domain.datamap import DatamapLine, DatamapLineValueType
from engine.domain.template import TemplateCell
from engine.utils.extraction import datamap_reader


@dataclass
class ParsedCell:
    sheetname: str
    cellref: str
    type: Optional[str]
    cell_value: str
    real_value: Union[str, float, int]

    def __repr__(self) -> str:
        return "<ParsedCell {} - {}>".format(self.cellref, self.sheetname)


WORKSHEET_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
)

CELL_VALUE_MAP = Dict[str, str]
EXTRACTED_FILE = DefaultDict[Path, Dict[str, List[TemplateCell]]]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)


class SpreadsheetReader:
    """Reads a spreadsheet and contains its read data.
    """

    # namespaces from the XML spec
    ns = {
        "d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "dcontent": "http://schemas.openxmlformats.org/package/2006/content-types",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    }

    def __init__(self, template: Path, datamap=None) -> None:
        self.fn = template
        self.datamap = datamap
        self.archive = zipfile.ZipFile(self.fn, "r")
        self.valid_files = self.archive.namelist()
        self.shared_strings: List[str] = []
        self._get_worksheet_files()
        self._get_worksheet_names()
        self._get_shared_strings()

    def _get_shared_strings(self) -> None:
        src = self.archive.read("xl/sharedStrings.xml")
        root = etree.fromstring(src)
        self.shared_strings = root.xpath(
            "d:si/d:t/text()", namespaces=SpreadsheetReader.ns
        )

    def _make_template_cell_dict(self, data, filename, sheetname):
        out = []
        del data["sheetname"]
        for x in data.items():
            out.append(
                (
                    x[0],
                    {
                        "cellref": x[0],
                        "data_type": "TEXT",
                        "file_name": filename,
                        "sheet_name": sheetname,
                        "value": x[1],
                    },
                )
            )
        return out

    def read_without_datamap(self):
        hash_ = hashlib.md5(open(self.fn, "rb").read()).digest().hex()
        sheets = self.sheet_names
        vals = [
            self.get_cell_values(sheetname)
            for sheetname in sheets
            if self.get_cell_values(sheetname) is not None
        ]
        base_dict = {"checksum": hash_, "data": {}}
        for sheet_data in vals:
            # Need to formulate the TemplateCell obj here
            s_name = sheet_data["sheetname"]
            cellmap = {}
            cellmap.update(
                self._make_template_cell_dict(sheet_data, self.fn.parts[-1], s_name)
            )
            sheetmap = {s_name: cellmap}
            base_dict["data"].update(sheetmap)
        return {self.fn.parts[-1]: base_dict}

    def _conv_xml_type_to_datamaplinevaluetype(self, val):
        if val in ["s", "str"]:
            return DatamapLineValueType.TEXT
        elif val == "t":
            return DatamapLineValueType.NUMBER

    def read(self) -> EXTRACTED_FILE:
        """Reads data from the template, given a list of DatamapLine objects.

        Returns a dict, whose key is the path to the template file. Each
        sheet is a sub-dict within.  The actual data is a list of TemplateCell
        objects.
        """
        dm_data = datamap_reader(self.datamap)
        sheets = self.sheet_names
        vals = [
            self.get_cell_values(sheetname)
            for sheetname in sheets
            if self.get_cell_values(sheetname) is not None
        ]
        cell_refs_in_dm = {d.cellref for d in dm_data}
        dt: EXTRACTED_FILE = defaultdict(lambda: defaultdict(list))
        for sheet_data in vals:
            sheet_name = sheet_data["sheetname"]
            for c in cell_refs_in_dm:
                if c in sheet_data.keys():
                    dt[self.fn][sheet_name].append(
                        TemplateCell(self.fn, sheet_name, c, sheet_data[c],)
                    )
        return dt

    def _get_worksheet_files(self) -> None:
        src = self.archive.read("[Content_Types].xml")
        root = etree.fromstring(src)
        self.worksheet_files = root.xpath(
            "dcontent:Override[@ContentType='"
            + WORKSHEET_CONTENT_TYPE
            + "']/@PartName",
            namespaces=SpreadsheetReader.ns,
        )

    def _get_sheet_rId(self, sheetname: str) -> str:
        src = self.archive.read("xl/workbook.xml")
        tree = etree.fromstring(src)
        lst_of_rid: List[str] = tree.xpath(  # type:ignore
            "d:sheets/d:sheet[@name='" + sheetname + "']/@r:id",
            namespaces=SpreadsheetReader.ns,
        )
        if len(lst_of_rid) == 0:
            raise ValueError("Cannot find sheet: {}".format(sheetname))
        else:
            return lst_of_rid[0]

    def _get_worksheet_path_from_rId(self, rid: str) -> str:
        src = self.archive.read("xl/_rels/workbook.xml.rels")
        tree = etree.fromstring(src)
        return tree.xpath(  # type: ignore
            "pr:Relationship[@Id='" + rid + "']/@Target",
            namespaces=SpreadsheetReader.ns,
        )[0]

    def _get_worksheet_names(self) -> None:
        src = self.archive.read("xl/workbook.xml")
        tree = etree.fromstring(src)
        self.sheet_names = tree.xpath(
            "d:sheets/d:sheet/@name", namespaces=SpreadsheetReader.ns
        )

    def get_cell_value(self, *, cellref: str, sheetname: str) -> Optional[str]:
        """Returns the value of cell at cellref in sheet sheetname.

        Returns None if the cell is not in range, or contains no value.
        """
        rid: str = self._get_sheet_rId(sheetname)
        path: str = self._get_worksheet_path_from_rId(rid)
        src = self.archive.read("".join(["xl/", path]))
        tree = etree.fromstring(src)
        lst_of_c_tags = tree.xpath(
            "d:sheetData/d:row/d:c[@r='" + cellref + "']/d:v",
            namespaces=SpreadsheetReader.ns,
        )
        if len(lst_of_c_tags) == 0:
            return None
        else:
            idx = int(
                tree.xpath(
                    "d:sheetData/d:row/d:c[@r='" + cellref + "']/d:v",
                    namespaces=SpreadsheetReader.ns,
                )[0].text
            )
            return self.shared_strings[idx]

    def get_cell_values(self, sheetname: str) -> Dict[str, str]:
        """Given a sheet name, will return a dictionary of cellname: value mappings.
        """
        rid: str = self._get_sheet_rId(sheetname)
        path: str = self._get_worksheet_path_from_rId(rid)
        src: bytes = self.archive.read("".join(["xl/", path]))
        tree: Element = etree.fromstring(src)
        out = {
            "sheetname": sheetname
        }  # rather than nest the dict here we put the sheetname in as a dict
        vcells: List[Element] = tree.xpath(
            "d:sheetData/d:row/d:c/d:v", namespaces=SpreadsheetReader.ns
        )
        for cell in vcells:  # go looking for value cells
            parent = cell.getparent()
            t = parent.attrib.get("t")
            if t is None:
                parsed_cell = ParsedCell(
                    sheetname,
                    cellref=parent.attrib.get("r"),
                    type=None,
                    cell_value=cell.text,
                    real_value="",
                )
            else:
                parsed_cell = ParsedCell(
                    sheetname,
                    cellref=parent.attrib.get("r"),
                    type=parent.attrib.get("t"),
                    cell_value=cell.text,
                    real_value="",
                )
            if parsed_cell.type == "s":  # we need to look up the string
                v = self.shared_strings[int(parsed_cell.cell_value)]
            elif parsed_cell.type == "str":  # value is in the v tag
                v = parsed_cell.cell_value
            elif parsed_cell.type == "n":  # a number
                try:
                    # int
                    v = int(parsed_cell.cell_value)  # type: ignore
                except ValueError:
                    # float
                    v = float(parsed_cell.cell_value)  # type: ignore
            parsed_cell.real_value = v
            out.update({parsed_cell.cellref: parsed_cell.real_value})
        return out


def template_reader_lxml(template_file):
    f_path: Path = Path(template_file)
    try:
        reader = SpreadsheetReader(template_file)
    except TypeError:
        msg = (
            "Unable to open {}. Potential corruption of file. Try resaving "
            "in Excel or removing conditional formatting. See issue at "
            "https://github.com/hammerheadlemon/bcompiler-engine/issues/3 for update. Quitting.".format(
                f_path
            )
        )
        logger.critical(msg)
        raise
    except BadZipFile:
        logger.critical(
            f"Cannot open {template_file} due to file not conforming to expected format. "
            f"Not continuing. Remove file from input directory and try again."
        )
        raise RuntimeError
    return reader.read_without_datamap()


# retain for posterity regarding doing this the basic way
#
# def get_sheet_names(xlsx_file):
#    f = open(xlsx_file, "rb")
#    data = f.read()
#    file_obj = io.BytesIO(data)
#    ns = {"d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
#    with zipfile.ZipFile(file_obj) as thezip:
#        with thezip.open("xl/workbook.xml") as wbxml:
#            tree = etree.parse(wbxml)

#            # Original way - returns single element
#            # sheets_a = root.find(
#            #     "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets"
#            # )

#            # Then we would need to use a list comp to get the name attribute.
#            #
#            # No need for this - we should use xpath
#            # return [x[0] for x in [sheet.values() for sheet in sheets]]

#            # xpath is much easier!
#            return tree.xpath("d:sheets/d:sheet/@name", namespaces=ns)

import zipfile
from typing import Dict, List, Optional

from lxml import etree
from lxml.etree import Element

WORKSHEET_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
)

CELL_VALUE_MAP = Dict[str, str]


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

    def __init__(self, file_name) -> None:
        self.fn = file_name
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

    def get_cell_values(self, sheetname: str) -> CELL_VALUE_MAP:
        """Given a sheet name, will return a dictionary of cellname: value mappings.
        """
        rid: str = self._get_sheet_rId(sheetname)
        path: str = self._get_worksheet_path_from_rId(rid)
        src: bytes = self.archive.read("".join(["xl/", path]))
        tree: Element = etree.fromstring(src)
        cells: List[Element] = tree.xpath(
            "d:sheetData/d:row/d:c", namespaces=SpreadsheetReader.ns
        )
        out = {
            "sheetname": sheetname
        }  # rather than nest the dict here we put the sheetname in as a dict
        for child in cells:  # go looking for value cells
            cellref = child.attrib["r"]
            child_tags = child.getchildren()
            if not child_tags:
                out.update(
                    {cellref: None}
                )  # if there is no <v> cell we put None in for cellref
            else:
                c_type = child.attrib["t"]

                # we need to distinguish between <f> and <v> tags
                # <v> contains the value, <f> the formula

                if len(child_tags) == 1:  # if only one, it is the <v> tag
                    if c_type == "s":  # we need to look up the string
                        v = self.shared_strings[int(child_tags[0].text)]
                    elif c_type == "str":  # value is in the v tag
                        v = child_tags[0].text
                    elif c_type == "n":  # a number
                        try:
                            # int
                            v = int(child_tags[0].text)  # type: ignore
                        except ValueError:
                            # float
                            v = float(child_tags[0].text)  # type: ignore
                    out.update({cellref: v})
                else:
                    # we have more than one child tag, which means a <f> and <v> tag
                    vtag = [
                        t
                        for t in child_tags
                        if t.tag
                        == "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v"
                    ][0]
                    if c_type == "s":
                        v = self.shared_strings[int(vtag.text)]
                    elif c_type == "str":
                        v = vtag.text
                    elif c_type == "n":
                        try:
                            # int
                            v = int(child_tags[1].text)  # type: ignore
                        except ValueError:
                            # float
                            v = float(child_tags[1].text)  # type: ignore
                    out.update({cellref: v})
        return out


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

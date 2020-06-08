import zipfile

from lxml import etree

WORKSHEET_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
)


class SpreadsheetReader:
    def __init__(self, file_name):
        self.fn = file_name
        self.archive = zipfile.ZipFile(self.fn, "r")
        self.valid_files = self.archive.namelist()
        self.shared_strings = []
        self._get_worksheet_files()
        self._get_worksheet_names()
        self._get_shared_strings()

    # def read_manifest(self):
    #     src = self.archive.read("[Content_Types].xml")
    #     root = etree.fromstring(src)
    #     self.package = None

    def _get_shared_strings(self):
        ns = {"d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        src = self.archive.read("xl/sharedStrings.xml")
        root = etree.fromstring(src)
        self.shared_strings = root.xpath("d:si/d:t/text()", namespaces=ns)

    def _get_worksheet_files(self):
        ns = {"d": "http://schemas.openxmlformats.org/package/2006/content-types"}
        src = self.archive.read("[Content_Types].xml")
        root = etree.fromstring(src)
        self.worksheet_files = root.xpath(
            "d:Override[@ContentType='" + WORKSHEET_CONTENT_TYPE + "']/@PartName",
            namespaces=ns,
        )

    def _get_sheet_rId(self, sheetname):
        ns = {
            "d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }
        src = self.archive.read("xl/workbook.xml")
        tree = etree.fromstring(src)
        return tree.xpath(
            "d:sheets/d:sheet[@name='" + sheetname + "']/@r:id", namespaces=ns
        )[0]

    def _get_worksheet_path_from_rId(self, rid):
        ns = {"d": "http://schemas.openxmlformats.org/package/2006/relationships"}
        src = self.archive.read("xl/_rels/workbook.xml.rels")
        tree = etree.fromstring(src)
        return tree.xpath("d:Relationship[@Id='" + rid + "']/@Target", namespaces=ns)[0]

    def _get_worksheet_names(self):
        ns = {"d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        src = self.archive.read("xl/workbook.xml")
        tree = etree.fromstring(src)
        self.sheet_names = tree.xpath("d:sheets/d:sheet/@name", namespaces=ns)

    def get_cell_value(self, cellref: str, sheetname: str):
        ns = {
            "d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }
        rid = self._get_sheet_rId(sheetname)
        path = self._get_worksheet_path_from_rId(rid)
        src = self.archive.read("".join(["xl/", path]))
        tree = etree.fromstring(src)
        idx = int(
            tree.xpath(
                "d:sheetData/d:row/d:c[@r='" + cellref + "']/d:v", namespaces=ns
            )[0].text
        )
        return self.shared_strings[idx]

    def get_cell_values(self, sheetname: str):
        ns = {
            "d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }
        rid = self._get_sheet_rId(sheetname)
        path = self._get_worksheet_path_from_rId(rid)
        src = self.archive.read("".join(["xl/", path]))
        tree = etree.fromstring(src)
        cells = tree.xpath("d:sheetData/d:row/d:c", namespaces=ns)
        out = {}
        for child in cells:
            cellref = child.attrib["r"]
            children = child.getchildren()
            if children:
                c_type = child.attrib["t"]
                kids = [ch for ch in children]
                if len(kids) == 1:
                    if c_type == "s":
                        v = self.shared_strings[int(kids[0].text)]
                    elif c_type == "str":
                        v = kids[0].text
                    elif c_type == "n":
                        try:
                            # int
                            v = int(kids[0].text)
                        except ValueError:
                            # float
                            v = float(kids[0].text)
                    out.update({cellref: v})
                else:
                    vtag = [
                        x
                        for x in kids
                        if x.tag
                        == "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v"
                    ][0]
                    if c_type == "s":
                        v = self.shared_strings[int(vtag.text)]
                    elif c_type == "str":
                        v = vtag.text
                    elif c_type == "n":
                        v = int(vtag.text)
                    out.update({cellref: v})
            else:
                out.update({cellref: None})
        return out

        # nodes = tree.xpath("d:sheetData/d:row/d:c/d:v/text()", namespaces=ns)
        # vals = tree.xpath("d:sheetData/d:row/d:c/d:v/text()", namespaces=ns)
        # cellrefs = tree.xpath("d:sheetData/d:row/d:c/@r", namespaces=ns)


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

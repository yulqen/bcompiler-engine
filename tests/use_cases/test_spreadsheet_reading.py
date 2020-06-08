import io
import zipfile
from pathlib import Path

import pytest
from lxml import etree
from openpyxl import load_workbook


@pytest.fixture
def xml_test_file() -> Path:
    return Path.cwd() / "tests" / "resources" / "test.xml"


WORKSHEET_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
)


class ExcelReader:
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


def get_sheet_names(xlsx_file):
    f = open(xlsx_file, "rb")
    data = f.read()
    file_obj = io.BytesIO(data)
    ns = {"d": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(file_obj) as thezip:
        with thezip.open("xl/workbook.xml") as wbxml:
            tree = etree.parse(wbxml)

            # Original way - returns single element
            # sheets_a = root.find(
            #     "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets"
            # )

            # Then we would need to use a list comp to get the name attribute.
            #
            # No need for this - we should use xpath
            # return [x[0] for x in [sheet.values() for sheet in sheets]]

            # xpath is much easier!
            return tree.xpath("d:sheets/d:sheet/@name", namespaces=ns)


def test_basic_xml_read(xml_test_file):
    tree = etree.parse(str(xml_test_file))
    assert (
        tree.getroot().tag
        == "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}workbook"
    )


def test_excel_reader_class(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert isinstance(reader.archive, zipfile.ZipFile)


def test_excel_reader_class_file_list(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert "xl/workbook.xml" in reader.valid_files


def test_excel_reader_class_has_package(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert "/xl/worksheets/sheet22.xml" in reader.worksheet_files


def test_excel_reader_class_can_get_sheet_names(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert reader.sheet_names[0] == "Introduction"


def test_excel_reader_class_can_get_shared_strings(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert reader.shared_strings[0] == "Fantastic Portfolio Collection Sheet"


def test_excel_reader_class_can_get_rel_for_worksheet(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert reader._get_sheet_rId("Introduction") == "rId3"
    assert reader._get_sheet_rId("Contents") == "rId4"


def test_excel_reader_class_can_get_worksheet_path_from_rId(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert reader._get_worksheet_path_from_rId("rId3") == "worksheets/sheet1.xml"


def test_get_cell_value_for_cellref_sheet_lxml(org_test_files_dir):
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    reader = ExcelReader(tmpl_file)
    assert reader.get_cell_value("C10", "Introduction") == "Coal Tits Ltd"
    assert (
        reader.get_cell_value("C9", "Introduction")
        == "Institute of Hairdressing Dophins"
    )


def test_bc_func_can_get_spreadsheet_file_sheet_names(org_test_files_dir):
    """
    Requisite bit of xl/workbook.xml (and referenced in p66 of IEC29500-1:2016(E)

    <sheet name="Introduction" sheetId="1" state="visible" r:id="rId3"/>
    <sheet name="Contents" sheetId="2" state="visible" r:id="rId4"/>
    <sheet name="Report Summary" sheetId="3" state="visible" r:id="rId5"/>
    <sheet name="GDPR - New SRO PDs" sheetId="4" state="hidden" r:id="rId6"/>
    <sheet name="Data Quality Log" sheetId="5" state="hidden" r:id="rId7"/>
    <sheet name="Dropdown List" sheetId="6" state="hidden" r:id="rId8"/>
    <sheet name="Data Triangulation" sheetId="7" state="hidden" r:id="rId9"/>
    <sheet name="Changes Since last Qtr" sheetId="8" state="hidden" r:id="rId10"/>
    <sheet name="To DO" sheetId="9" state="hidden" r:id="rId11"/>
    <sheet name="Flat File" sheetId="10" state="hidden" r:id="rId12"/>
    <sheet name="Query DB" sheetId="11" state="hidden" r:id="rId13"/>
    <sheet name="Flat file checking" sheetId="12" state="hidden" r:id="rId14"/>
    <sheet name="1 - Project Info" sheetId="13" state="visible" r:id="rId15"/>
    <sheet name="2 - DCA &amp; Risk" sheetId="14" state="visible" r:id="rId16"/>
    <sheet name="3 - Scope History" sheetId="15" state="visible" r:id="rId17"/>
    <sheet name="4 - Leaders" sheetId="16" state="visible" r:id="rId18"/>
    <sheet name="5 - People" sheetId="17" state="visible" r:id="rId19"/>
    <sheet name="6a - Milestones - Approvals" sheetId="18" state="visible" r:id="rId20"/>
    <sheet name="6b - Milestones - Assurance" sheetId="19" state="visible" r:id="rId21"/>
    <sheet name="6c - Milestones - Delivery" sheetId="20" state="visible" r:id="rId22"/>
    <sheet name="7 - Business Case" sheetId="21" state="visible" r:id="rId23"/>
    <sheet name="8 - Finance" sheetId="22" state="visible" r:id="rId24"/>
    <sheet name="9 - Costs" sheetId="23" state="visible" r:id="rId25"/>
    <sheet name="10 - Benefits" sheetId="24" state="visible" r:id="rId26"/>
    <sheet name="Tab 12 - Annual Report" sheetId="25" state="hidden" r:id="rId27"/>
    <sheet name="Drop Downs" sheetId="26" state="hidden" r:id="rId28"/>
    """

    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    assert get_sheet_names(tmpl_file)[0] == "Introduction"
    assert get_sheet_names(tmpl_file)[1] == "Contents"


@pytest.mark.skip("used for exploring openpyxl")
def test_straight_read_using_openpyxl(org_test_files_dir):
    """The test template file here is full-sized and full of formatting.

    load_workbook() is very slow. Run with --profile
    """
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    breakpoint()
    data = load_workbook(tmpl_file)

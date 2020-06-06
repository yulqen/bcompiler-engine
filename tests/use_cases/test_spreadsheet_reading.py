import io
import pytest
from pathlib import Path
import zipfile
from openpyxl import load_workbook
from lxml import etree


@pytest.fixture
def xml_test_file() -> Path:
    return Path.cwd() / "tests" / "resources" / "test.xml"


def get_sheet_names(xlsx_file):
    f = open(xlsx_file, "rb")
    data = f.read()
    file_obj = io.BytesIO(data)
    with zipfile.ZipFile(file_obj) as thezip:
        with thezip.open("xl/workbook.xml") as wbxml:
            x_data = wbxml.read()
            root = etree.fromstring(x_data)
            sheets = root[4].getchildren()
            s1 = sheets[0]
            breakpoint()
            for elem in root.getchildren():
                if not elem.text:
                    text = "None"
                else:
                    text = elem.text
                print(elem.tag + " => " + text)
            pass


def test_basic_xml_read(xml_test_file):
    tree = etree.parse(str(xml_test_file))
    assert (
        tree.getroot().tag
        == "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}workbook"
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


def test_straight_read_using_openpyxl(org_test_files_dir):
    """The test template file here is full-sized and full of formatting.

    load_workbook() is very slow. Run with --profile
    """
    tmpl_file = org_test_files_dir / "dft1_tmp.xlsm"
    data = load_workbook(tmpl_file)

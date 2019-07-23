import pytest

from engine.domain.datamap import DatamapLineValueType
from engine.domain.template import TemplateCell
from engine.utils.extraction import _clean, _extract_cellrefs


def test_send_wrong_type_to_clean():
    with pytest.raises(TypeError):
        _clean(2)


@pytest.mark.skip("Not ready")
def test_throw_exception_when_find_duplicate_values():
    """This function should never find TemplateCell objects containing
    identical sheet/cellref combinations, and should throw a RuntimeError.
    """
    tc1 = TemplateCell("test_file.xlsx", "Sheet 1", "A1", "Test Value 1", DatamapLineValueType.TEXT)
    tc2 = TemplateCell("test_file.xlsx", "Sheet 1", "A1", "Test Value 2", DatamapLineValueType.TEXT)
    result = _extract_cellrefs([tc1, tc2])

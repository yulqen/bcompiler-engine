import pytest

from engine.utils.extraction import _clean


def test_send_wrong_type_to_clean():
    with pytest.raises(TypeError):
        _clean(2)

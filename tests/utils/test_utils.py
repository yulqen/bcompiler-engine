import pytest

from engine.utils.extraction import _clean


def test_send_none_to_clean():
    with pytest.raises(
        AttributeError, match=r"Cannot clean value other than a string here*."
    ):
        _clean(None)


def test_send_int_to_clean():
    with pytest.raises(
        AttributeError, match=r"Cannot clean value other than a string here*."
    ):
        _clean(2)

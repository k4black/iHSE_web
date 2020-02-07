import pytest

from backend import main


def test_groupby():
    assert len(main.TODAY) == 5
    assert main.TODAY[2] == '.'



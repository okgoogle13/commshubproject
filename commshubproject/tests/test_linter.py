# ### FILE: commshubproject/tests/test_linter.py
from src.linter import Linter

def test_linter_shame_cascade():
    linter = Linter()
    res = linter.check_draft("This is a shame cascade waiting to happen.")
    assert not res["passed"]
    assert "SHAME CASCADE" in res["flags"]

def test_linter_unverified_promise():
    linter = Linter()
    res = linter.check_draft("I promise to have it done.")
    assert not res["passed"]
    assert "UNVERIFIED PROMISE" in res["flags"]

def test_linter_clean():
    linter = Linter()
    res = linter.check_draft("I will look into it.")
    assert res["passed"]

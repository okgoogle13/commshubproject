from src.linter import Linter


def test_linter_shame_cascade_explicit():
    linter = Linter()
    res = linter.check_draft("I'm so sorry for ignoring you.")
    assert not res["passed"]
    assert any("sorry" in f.lower() for f in res["flags"])


def test_linter_shame_cascade_worst():
    linter = Linter()
    res = linter.check_draft("I'm the worst daughter ever.")
    assert not res["passed"]


def test_linter_promise_phrase():
    linter = Linter()
    res = linter.check_draft("I promise I'll call you soon.")
    assert not res["passed"]
    assert "I promise I'll" in res["flags"]


def test_linter_day_time_promise():
    linter = Linter()
    res = linter.check_draft("I'll call you Sunday at 7pm, ok?")
    assert not res["passed"]
    assert any("sunday" in f.lower() or "specific" in f.lower() or "time" in f.lower() for f in res["flags"])


def test_linter_formal_signoff():
    linter = Linter()
    res = linter.check_draft("Looking forward to catching up. Kind regards, Jonas")
    assert not res["passed"]


def test_linter_vague_intention_ok():
    linter = Linter()
    res = linter.check_draft("Will try to call this weekend. Love you both xx")
    assert res["passed"]


def test_linter_clean_minimal():
    linter = Linter()
    res = linter.check_draft("Hey, saw this — will be in touch. xx")
    assert res["passed"]


def test_linter_clean_honest():
    linter = Linter()
    res = linter.check_draft("I know it's been ages. Brain's been a bit frozen, not my love for you. Thinking of you both xx")
    assert res["passed"]

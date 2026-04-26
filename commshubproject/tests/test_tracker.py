import os
import time
import pytest
from src.tracker import Tracker

TEST_DB = "/tmp/commshub_test.db"
TEST_KEY = "testkey12345678901234567890123"


@pytest.fixture(autouse=True)
def clean_db():
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def get_tracker():
    return Tracker(db_path=TEST_DB, encryption_key=TEST_KEY)


def test_record_inbound():
    t = get_tracker()
    t.record_inbound(
        message_id="msg001",
        contact_token="MUM",
        imessage_handle="molly.dougall@icloud.com",
        redacted_text="Hey [REDACTED_MUM], are you coming?",
        received_at=1714200000,
    )
    rows = t.get_pending_inbounds()
    assert len(rows) == 1
    assert rows[0]["message_id"] == "msg001"
    assert rows[0]["status"] == "pending"


def test_record_draft():
    t = get_tracker()
    t.record_inbound("msg002", "MUM", "molly@x.com", "test", 1714200000)
    t.record_draft(
        "msg002",
        "minimal_draft",
        "honest_draft",
        "practical_draft",
        "freeform",
        "freeform",
        "freeform",
    )
    rows = t.get_pending_inbounds()
    assert len(rows) == 1
    assert rows[0]["status"] == "drafted"


def test_mark_sent():
    t = get_tracker()
    t.record_inbound("msg003", "DAD", "dad@x.com", "test", 1714200000)
    t.record_draft("msg003", "m", "h", "p", "freeform", "freeform", "freeform")
    t.mark_sent("msg003", "minimal", "m", str(time.time()))
    rows = t.get_pending_inbounds()
    assert len(rows) == 0


def test_mark_skipped():
    t = get_tracker()
    t.record_inbound("msg004", "MUM", "mum@x.com", "test", 1714200000)
    t.mark_skipped("msg004", reason="not relevant")
    rows = t.get_pending_inbounds()
    assert len(rows) == 0


def test_is_known_message():
    t = get_tracker()
    assert not t.is_known_message("nope")
    t.record_inbound("msg005", "MUM", "mum@x.com", "test", 1714200000)
    assert t.is_known_message("msg005")


def test_days_since_last_sent_no_history():
    t = get_tracker()
    days = t.days_since_last_sent("MUM")
    assert days == 999


def test_days_since_last_sent_with_history():
    t = get_tracker()
    t.record_inbound("msg006", "MUM", "mum@x.com", "test", 1714200000)
    t.record_draft("msg006", "m", "h", "p", "f", "f", "f")
    t.mark_sent("msg006", "minimal", "m", str(time.time()))
    days = t.days_since_last_sent("MUM")
    assert isinstance(days, float)
    assert 0 <= days < 1


def test_status_summary():
    t = get_tracker()
    t.record_inbound("msg007", "DAD", "dad@x.com", "test", 1714200000)
    summary = t.get_status_summary()
    assert summary["pending"] == 1
    assert summary["total_sent"] == 0

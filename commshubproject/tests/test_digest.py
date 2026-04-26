import time
from unittest.mock import MagicMock
from src.digest import Digest, sort_pending_items


def _item(msg_id, contact, days_old, has_draft=True, status="drafted"):
    received = int(time.time()) - (days_old * 86400)
    return {
        "message_id": msg_id,
        "contact_token": contact,
        "imessage_handle": f"{contact.lower()}@example.com",
        "redacted_text": f"Test message from {contact}",
        "received_at": received,
        "status": status,
        "draft_minimal": "Hi xx" if has_draft else None,
        "draft_honest": "Sorry, brain frozen. xx" if has_draft else None,
        "draft_practical": "Can we talk this weekend? xx" if has_draft else None,
    }


def test_sort_puts_oldest_first():
    items = [
        _item("a", "MUM", 5),
        _item("b", "DAD", 80),
        _item("c", "MUM", 3),
    ]
    sorted_items = sort_pending_items(items)
    assert sorted_items[0]["message_id"] == "b"


def test_sort_old_operational_before_recent():
    items = [
        _item("recent", "MUM", 2),
        _item("very_old", "DAD", 100),
    ]
    result = sort_pending_items(items)
    assert result[0]["message_id"] == "very_old"


def test_format_item_shows_three_options():
    digest = Digest(tracker=MagicMock())
    item = _item("x", "MUM", 11)
    formatted = digest.format_item(item)
    assert "[1] Minimal" in formatted
    assert "[2] Honest" in formatted
    assert "[3] Practical" in formatted
    assert "MUM" in formatted
    assert "11" in formatted


def test_format_item_draft_unavailable():
    digest = Digest(tracker=MagicMock())
    item = _item("y", "DAD", 3, has_draft=False, status="pending")
    formatted = digest.format_item(item)
    assert "DRAFT UNAVAILABLE" in formatted
    assert "[1]" not in formatted


def test_run_interactive_no_pending(capsys):
    tracker = MagicMock()
    tracker.get_pending_inbounds.return_value = []
    digest = Digest(tracker=tracker)
    digest.run_interactive()
    out = capsys.readouterr().out
    assert "No pending items" in out

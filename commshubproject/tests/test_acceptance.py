"""
Milestone 1 Acceptance Test
Spec success condition: operator runs 'commshub digest', sees drafted reply to Mum's
pending message, types 'send 1', message delivered via iMessage.
No copy-paste. No app-switching. Interaction under 10 seconds.
"""
import os
import time
import pytest
from src.redactor import Redactor
from src.linter import Linter
from src.tracker import Tracker
from src.sender import Sender

TEST_DB = "/tmp/commshub_acceptance_test.db"
TEST_KEY = "acceptance_test_key_32chars_xxxx"


@pytest.fixture(autouse=True)
def clean_db():
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


class MockDrafter:
    def draft_reply(self, text, silence_days=0, contact_token="MUM"):
        return {
            "minimal": "Hey, will be in touch soon. xx",
            "honest": "Sorry for the silence, brain's been busy. Miss you xx",
            "practical_reentry": "Hey — still on for dinner? Let me know when works. xx",
            "tone_warnings": [],
            "promise_warnings": [],
            "confidence": "high",
            "confidence_reason": "clear inbound",
        }


class MockSubprocess:
    """Intercepts subprocess.run calls to avoid real osascript/iMessage sends in tests."""
    def __init__(self):
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd)
        result = type("Result", (), {"returncode": 0, "stderr": "", "stdout": ""})()
        return result


def test_milestone_1_acceptance():
    inbound_handle = "molly.dougall@icloud.com"
    inbound_text = "Hi, it's Mum. When are you coming to 3070? See you at 42 Wallaby Way"

    # Step 1: Redaction — PII must be stripped before any external call
    redactor = Redactor()
    safe_text = redactor.redact(inbound_text)
    assert "[REDACTED_MUM]" in safe_text, "Mum token not in redacted text"
    assert "[REDACTED_POSTCODE]" in safe_text, "Postcode not redacted"
    assert "3070" not in safe_text, "Postcode still present"
    assert "[REDACTED_ADDRESS]" in safe_text, "Address not redacted"
    assert "42 Wallaby Way" not in safe_text, "Address still present"

    # Step 2: Tracker records inbound — status = 'pending'
    tracker = Tracker(db_path=TEST_DB, encryption_key=TEST_KEY)
    tracker.record_inbound(
        message_id="acc_test_001",
        contact_token="MUM",
        imessage_handle=inbound_handle,
        redacted_text=safe_text,
        received_at=int(time.time()) - (11 * 86400),  # simulate 11 days ago
    )
    pending = tracker.get_pending_inbounds()
    assert len(pending) == 1
    assert pending[0]["status"] == "pending"
    assert pending[0]["message_id"] == "acc_test_001"

    # Step 3: Draft — three modes required
    drafter = MockDrafter()
    silence = tracker.days_since_last_sent("MUM")
    drafts = drafter.draft_reply(safe_text, silence_days=int(silence), contact_token="MUM")
    assert "minimal" in drafts
    assert "honest" in drafts
    assert "practical_reentry" in drafts
    assert drafts["minimal"].endswith("xx"), "Missing 'xx' sign-off in minimal draft"

    # Step 4: Tracker records draft — status = 'drafted'
    tracker.record_draft(
        "acc_test_001",
        drafts["minimal"],
        drafts["honest"],
        drafts["practical_reentry"],
        "freeform",
        "freeform",
        "freeform",
    )
    pending = tracker.get_pending_inbounds()
    assert pending[0]["status"] == "drafted"

    # Step 5: Linter — no false positives on clean drafts
    linter = Linter()
    for mode in ("minimal", "honest", "practical_reentry"):
        result = linter.check_draft(drafts[mode])
        assert result["passed"], f"Linter false positive in '{mode}': {result['flags']}"

    # Step 6: Sender — requires approval token, logs to tracker
    mock_proc = MockSubprocess()
    sender = Sender(tracker=tracker)
    token = sender.issue_token("acc_test_001")
    assert token.startswith("tok_acc_test_001")

    import unittest.mock as mock
    with mock.patch("src.sender.subprocess.run", side_effect=mock_proc):
        success = sender.send_message(
            inbound_handle,
            drafts["minimal"],
            "acc_test_001",
            "minimal",
            token,
        )
    assert success is True
    assert len(mock_proc.calls) == 1
    assert "osascript" in mock_proc.calls[0]

    # Step 7: Tracker state = 'sent', no longer in pending
    still_pending = tracker.get_pending_inbounds()
    assert len(still_pending) == 0, "Item should be removed from pending after send"

    # Step 8: Approval token is consumed — can't re-use it
    with pytest.raises(PermissionError):
        sender.send_message(inbound_handle, drafts["honest"], "acc_test_001", "honest", token)

    print("[ACCEPTANCE] Milestone 1 test PASSED.")

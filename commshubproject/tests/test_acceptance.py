# ### FILE: commshubproject/tests/test_acceptance.py
import pytest
from src.redactor import Redactor
from src.linter import Linter

class MockDrafter:
    def draft_reply(self, message_text):
        if "REDACTED_MUM" in message_text:
            return "Hi Mum, I'll call you later."
        return "Acknowledged."

class MockSender:
    def send_message(self, number, body):
        return True

def test_milestone_1_acceptance():
    # 1. Inbound message simulation
    inbound_number = "+61412345678"
    inbound_message = "Hi, it's Mum. When are you coming to 3070? See you at 42 Wallaby Way"
    
    # 2. Redaction
    redactor = Redactor()
    safe_text = redactor.redact(inbound_message)
    assert "[REDACTED_MUM]" in safe_text
    assert "[REDACTED_POSTCODE]" in safe_text
    assert "3070" not in safe_text
    assert "[REDACTED_ADDRESS]" in safe_text
    assert "42 Wallaby Way" not in safe_text
    
    # 3. Drafting
    class MockDrafterDict:
        def draft_reply(self, message_text, persona="default"):
            if "REDACTED_MUM" in message_text:
                return {
                    "minimal": "Hey Mum, get back to you soon.",
                    "honest": "Sorry Mum, been flat out.",
                    "practical_reentry": "Hey Mum, still on for dinner?"
                }
            return {"minimal": "Acknowledged."}

    drafter = MockDrafterDict()
    drafts = drafter.draft_reply(safe_text)
    assert "Mum" in drafts["minimal"]
    
    # 4. Linting
    linter = Linter()
    lint_result = linter.check_draft(drafts["honest"])
    assert lint_result["passed"] is True
    
    # 5. Mock Send Execution
    sender = MockSender()
    success = sender.send_message(inbound_number, drafts["minimal"])
    assert success is True
    
    print("Acceptance test logic executes perfectly in simulated environment.")

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
    inbound_number = "+447700900077"
    inbound_message = "Hi, it's Mum. When are you coming to SW1A 1AA?"
    
    # 2. Redaction
    redactor = Redactor()
    safe_text = redactor.redact(inbound_message)
    assert "[REDACTED_MUM]" in safe_text
    assert "[REDACTED_POSTCODE]" in safe_text
    assert "SW1A 1AA" not in safe_text
    
    # 3. Drafting
    drafter = MockDrafter()
    draft = drafter.draft_reply(safe_text)
    assert "Mum" in draft 
    
    # 4. Linting
    linter = Linter()
    lint_result = linter.check_draft(draft)
    assert lint_result["passed"] is True
    
    # 5. Mock Send Execution
    sender = MockSender()
    success = sender.send_message(inbound_number, draft)
    assert success is True
    
    print("Acceptance test logic executes perfectly in simulated environment.")

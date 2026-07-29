# ### FILE: commshubproject/tests/test_redactor.py
from src.redactor import Redactor

def test_redactor_names():
    redactor = Redactor()
    res = redactor.redact("Call Mum and Dad about the party.")
    assert "[REDACTED_MUM]" in res
    assert "[REDACTED_DAD]" in res

def test_redactor_pii():
    redactor = Redactor()
    res = redactor.redact("My number is 0412 345 678 and postcode is 3070 at 42 Wallaby Way.")
    assert "[REDACTED_PHONE]" in res
    assert "[REDACTED_POSTCODE]" in res
    assert "[REDACTED_ADDRESS]" in res

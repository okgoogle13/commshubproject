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


def test_redactor_uk_phone_international():
    redactor = Redactor()
    res = redactor.redact("Call me on +44 7700 900077 please.")
    assert "[REDACTED_PHONE]" in res
    assert "+44 7700 900077" not in res


def test_redactor_uk_phone_local():
    redactor = Redactor()
    res = redactor.redact("My old UK number is 07700900077.")
    assert "[REDACTED_PHONE]" in res
    assert "07700900077" not in res


def test_redactor_email():
    redactor = Redactor()
    res = redactor.redact("My email is molly.dougall@icloud.com please reply there.")
    assert "[REDACTED_EMAIL]" in res
    assert "molly.dougall@icloud.com" not in res


def test_redactor_family_full_names():
    redactor = Redactor()
    res = redactor.redact("Molly and Arvind are coming to visit.")
    assert "Molly" not in res
    assert "Arvind" not in res


def test_redactor_imessage_handle():
    redactor = Redactor()
    res = redactor.redact("Reply to molly.dougall@icloud.com when you can.")
    assert "molly.dougall@icloud.com" not in res


def test_redactor_empty_returns_empty():
    redactor = Redactor()
    assert redactor.redact("") == ""
    assert redactor.redact(None) is None

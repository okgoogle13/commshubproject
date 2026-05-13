import pytest
from unittest.mock import patch, MagicMock
from src.drafter import Drafter

DUMMY_KEY = "test-key-000000000000000000000000"


def _make_drafter():
    """Instantiate Drafter with a dummy key, patching genai.Client so no real connection is made."""
    with patch("src.drafter.genai.Client"):
        return Drafter(api_key=DUMMY_KEY)


def _mock_response(text):
    m = MagicMock()
    m.text = text
    return m


def test_drafter_model_name():
    drafter = _make_drafter()
    assert "gemini-2.5-pro" in drafter.model_name


def test_drafter_returns_three_modes():
    drafter = _make_drafter()
    json_out = '{"minimal": "Hi xx", "honest": "Sorry for silence. Love you xx", "practical_reentry": "Still on for Sunday? xx"}'
    with patch.object(drafter.client.models, "generate_content", return_value=_mock_response(json_out)):
        result = drafter.draft_reply("test message", silence_days=5)
    assert result["minimal"] == "Hi xx"
    assert result["honest"] == "Sorry for silence. Love you xx"
    assert result["practical_reentry"] == "Still on for Sunday? xx"


def test_drafter_strips_json_fences():
    drafter = _make_drafter()
    fenced = '```json\n{"minimal": "a", "honest": "b", "practical_reentry": "c"}\n```'
    with patch.object(drafter.client.models, "generate_content", return_value=_mock_response(fenced)):
        result = drafter.draft_reply("test", silence_days=0)
    assert result["minimal"] == "a"


def test_drafter_handles_parse_error_gracefully():
    drafter = _make_drafter()
    with patch.object(drafter.client.models, "generate_content", return_value=_mock_response("not json at all")):
        result = drafter.draft_reply("test", silence_days=0)
    assert "Error" in result["minimal"]
    assert "minimal" in result
    assert "honest" in result
    assert "practical_reentry" in result


def test_drafter_passes_silence_days_in_prompt():
    drafter = _make_drafter()
    captured = []

    def capture(model, contents, config=None, **kwargs):
        captured.append(str(contents))
        return _mock_response('{"minimal": "x", "honest": "y", "practical_reentry": "z"}')

    with patch.object(drafter.client.models, "generate_content", side_effect=capture):
        drafter.draft_reply("hi mum", silence_days=14, contact_token="MUM")

    assert "14" in captured[0] or "silence" in captured[0].lower()

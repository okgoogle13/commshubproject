import pytest
from unittest.mock import patch, MagicMock
from src.drafter import Drafter


def _mock_response(text):
    m = MagicMock()
    m.text = text
    return m


def test_drafter_model_name():
    drafter = Drafter()
    assert "gemini-3.1-pro-preview" in drafter.model.model_name


def test_drafter_returns_three_modes():
    drafter = Drafter()
    json_out = '{"minimal": "Hi xx", "honest": "Sorry for silence. Love you xx", "practical_reentry": "Still on for Sunday? xx"}'
    with patch.object(drafter.model, "generate_content", return_value=_mock_response(json_out)):
        result = drafter.draft_reply("test message", silence_days=5)
    assert result["minimal"] == "Hi xx"
    assert result["honest"] == "Sorry for silence. Love you xx"
    assert result["practical_reentry"] == "Still on for Sunday? xx"


def test_drafter_strips_json_fences():
    drafter = Drafter()
    fenced = '```json\n{"minimal": "a", "honest": "b", "practical_reentry": "c"}\n```'
    with patch.object(drafter.model, "generate_content", return_value=_mock_response(fenced)):
        result = drafter.draft_reply("test", silence_days=0)
    assert result["minimal"] == "a"


def test_drafter_handles_parse_error_gracefully():
    drafter = Drafter()
    with patch.object(drafter.model, "generate_content", return_value=_mock_response("not json at all")):
        result = drafter.draft_reply("test", silence_days=0)
    assert "Error" in result["minimal"]
    assert "minimal" in result
    assert "honest" in result
    assert "practical_reentry" in result


def test_drafter_passes_silence_days_in_prompt():
    drafter = Drafter()
    captured = []

    def capture(prompt, **kwargs):
        captured.append(str(prompt))
        return _mock_response('{"minimal": "x", "honest": "y", "practical_reentry": "z"}')

    with patch.object(drafter.model, "generate_content", side_effect=capture):
        drafter.draft_reply("hi mum", silence_days=14, contact_token="MUM")

    assert "14" in captured[0] or "silence" in captured[0].lower()

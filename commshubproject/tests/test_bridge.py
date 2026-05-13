import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from commshub_bridge import app

client = TestClient(app)
MOCK_TARGET = "commshub_bridge._send_via_applescript"


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_valid_handle_sends():
    with patch(MOCK_TARGET) as mock_send:
        resp = client.post("/send-message", json={
            "handle": "molly.dougall@icloud.com",
            "message": "Hello xx",
            "mode": "test",
        })
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    mock_send.assert_called_once_with("molly.dougall@icloud.com", "Hello xx")


def test_valid_dad_handle_sends():
    with patch(MOCK_TARGET) as mock_send:
        resp = client.post("/send-message", json={
            "handle": "drarvinddougall@gmail.com",
            "message": "Hi xx",
            "mode": "test",
        })
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    mock_send.assert_called_once()


def test_case_insensitive_handle_accepted():
    with patch(MOCK_TARGET) as mock_send:
        resp = client.post("/send-message", json={
            "handle": "MOLLY.DOUGALL@ICLOUD.COM",
            "message": "Hi xx",
            "mode": "test",
        })
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    mock_send.assert_called_once()


def test_handle_not_in_allow_list():
    with patch(MOCK_TARGET) as mock_send:
        resp = client.post("/send-message", json={
            "handle": "notallowed@example.com",
            "message": "Hi",
            "mode": "test",
        })
    assert resp.status_code == 400
    assert resp.json() == {"ok": False, "error": "handle not in allow-list"}
    mock_send.assert_not_called()


def test_empty_message_rejected():
    with patch(MOCK_TARGET) as mock_send:
        resp = client.post("/send-message", json={
            "handle": "molly.dougall@icloud.com",
            "message": "   ",
            "mode": "test",
        })
    assert resp.status_code == 400
    assert resp.json() == {"ok": False, "error": "message is required"}
    mock_send.assert_not_called()


def test_missing_handle_rejected():
    with patch(MOCK_TARGET) as mock_send:
        resp = client.post("/send-message", json={
            "handle": "",
            "message": "Hi",
            "mode": "test",
        })
    assert resp.status_code == 400
    assert resp.json() == {"ok": False, "error": "handle is required"}
    mock_send.assert_not_called()


def test_applescript_runtime_error_returns_500():
    with patch(MOCK_TARGET, side_effect=RuntimeError("osascript failed")):
        resp = client.post("/send-message", json={
            "handle": "molly.dougall@icloud.com",
            "message": "Hi xx",
            "mode": "test",
        })
    assert resp.status_code == 500
    body = resp.json()
    assert body["ok"] is False
    assert "osascript failed" in body["error"]


def test_message_with_quotes_does_not_crash():
    """Regression: message containing double-quotes must not break AppleScript escaping."""
    with patch(MOCK_TARGET) as mock_send:
        resp = client.post("/send-message", json={
            "handle": "molly.dougall@icloud.com",
            "message": 'She said "hello" to me',
            "mode": "test",
        })
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    mock_send.assert_called_once_with("molly.dougall@icloud.com", 'She said "hello" to me')

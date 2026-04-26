from src.watcher import Watcher

ALLOW_LIST = [
    {"name": "Molly Dougall", "token": "MUM", "imessage_handle": "molly.dougall@icloud.com"},
    {"name": "Daddy Dougall", "token": "DAD", "imessage_handle": "drarvindougall@gmail.com"},
]


def test_filters_allow_list_only():
    w = Watcher(allow_list=ALLOW_LIST)
    raw = [
        {"handle": "molly.dougall@icloud.com", "message": "Hi love", "id": "1", "is_from_me": 0},
        {"handle": "unknown@example.com", "message": "spam", "id": "2", "is_from_me": 0},
        {"handle": "molly.dougall@icloud.com", "message": "sent by me", "id": "3", "is_from_me": 1},
    ]
    result = w.filter_inbounds(raw)
    assert len(result) == 1
    assert result[0]["id"] == "1"
    assert result[0]["contact_token"] == "MUM"


def test_skips_media_only_messages():
    w = Watcher(allow_list=ALLOW_LIST)
    raw = [
        {"handle": "molly.dougall@icloud.com", "message": "", "id": "4", "is_from_me": 0},
        {"handle": "molly.dougall@icloud.com", "message": None, "id": "5", "is_from_me": 0},
    ]
    result = w.filter_inbounds(raw)
    assert len(result) == 0


def test_attaches_dad_token():
    w = Watcher(allow_list=ALLOW_LIST)
    raw = [{"handle": "drarvindougall@gmail.com", "message": "hello", "id": "6", "is_from_me": 0}]
    result = w.filter_inbounds(raw)
    assert result[0]["contact_token"] == "DAD"


def test_case_insensitive_handle_matching():
    w = Watcher(allow_list=ALLOW_LIST)
    raw = [{"handle": "MOLLY.DOUGALL@ICLOUD.COM", "message": "hi", "id": "7", "is_from_me": 0}]
    result = w.filter_inbounds(raw)
    assert len(result) == 1
    assert result[0]["contact_token"] == "MUM"

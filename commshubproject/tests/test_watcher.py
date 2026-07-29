# ### FILE: commshubproject/tests/test_watcher.py
from src.watcher import Watcher

def test_watcher_initialization():
    watcher = Watcher("fake/path.db")
    assert "/fake/path.db" in watcher.db_path

def test_fetch_recent_messages():
    watcher = Watcher("fake/path.db")
    # Will likely return empty list due to no exist db, but shouldn't crash
    msgs = watcher.fetch_recent_messages(limit=5)
    assert isinstance(msgs, list)

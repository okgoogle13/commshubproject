# ### FILE: commshubproject/src/watcher.py
import os
from imessage_reader import fetch_data

class Watcher:
    def __init__(self, db_path="~/Library/Messages/chat.db"):
        self.db_path = os.path.expanduser(db_path)

    def fetch_recent_messages(self, limit=10):
        try:
            fd = fetch_data.FetchData(self.db_path)
            # Returns a list of tuples: (user_id, text, date, service, account, is_from_me)
            messages = fd.get_messages()
            if not messages:
                return []
            
            # Sort by date pseudo-logic (fetch_data generally sorts chronologically)
            # Take the newest `limit` messages
            return messages[-limit:]
        except Exception as e:
            print(f"Watcher Error: {e}")
            return []

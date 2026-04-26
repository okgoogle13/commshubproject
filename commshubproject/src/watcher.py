import os
import yaml


class Watcher:
    def __init__(self, allow_list=None, db_path=None):
        if allow_list is None:
            config_path = os.path.join(os.path.dirname(__file__), "../config/allow_list.yaml")
            with open(config_path) as f:
                data = yaml.safe_load(f)
            allow_list = data.get("allow_list", [])
        self.allow_list = allow_list
        self._handle_map = {c["imessage_handle"].lower(): c for c in allow_list}
        self.db_path = db_path or os.path.expanduser("~/Library/Messages/chat.db")

    def filter_inbounds(self, raw_messages):
        results = []
        for msg in raw_messages:
            handle = (msg.get("handle") or "").lower()
            text = msg.get("message") or ""
            if msg.get("is_from_me", 0) == 1:
                continue
            if not text.strip():
                continue
            if handle not in self._handle_map:
                continue
            contact = self._handle_map[handle]
            results.append({
                "id": msg["id"],
                "handle": handle,
                "contact_token": contact["token"],
                "contact_name": contact["name"],
                "message": text,
            })
        return results

    def fetch_and_filter(self):
        try:
            from imessage_reader import fetch_data
            fd = fetch_data.FetchData(self.db_path)
            raw = fd.get_messages()
            normalized = [
                {
                    "handle": m[0],
                    "message": m[1],
                    "id": str(hash(f"{m[0]}{m[1]}{m[2]}")),
                    "is_from_me": 0,
                }
                for m in raw
            ]
            return self.filter_inbounds(normalized)
        except Exception as e:
            print(f"[WATCHER] Error reading chat.db: {e}")
            return []

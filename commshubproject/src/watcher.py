import os
import sqlite3
import yaml

APPLE_EPOCH_OFFSET = 978307200  # seconds between Unix epoch (1970) and Apple epoch (2001)


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
        """
        Filter a list of raw message dicts against the allow_list.
        Each raw message must have: id, handle, message, is_from_me.
        received_at is passed through if present.
        """
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
                "received_at": msg.get("received_at"),
            })
        return results

    def fetch_and_filter(self, since_rowid=0):
        """
        Query chat.db directly for new inbound messages from allow-listed contacts.

        Uses the message ROWID (a stable, auto-incrementing integer from SQLite) as
        the message ID. Pass since_rowid to fetch only messages newer than the last
        poll — the caller (cli.py) is responsible for persisting this value via
        tracker.set_meta('last_rowid', ...).

        Returns a list of filtered message dicts, each containing:
            id, handle, contact_token, contact_name, message, received_at
        """
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    m.ROWID                  AS rowid,
                    m.text                   AS message,
                    m.is_from_me             AS is_from_me,
                    m.date                   AS apple_date,
                    m.cache_has_attachments  AS has_attachments,
                    h.id                     AS handle
                FROM message m
                JOIN handle h ON m.handle_id = h.ROWID
                WHERE m.is_from_me = 0
                  AND m.ROWID > ?
                ORDER BY m.ROWID ASC
            """, (since_rowid,))

            rows = cursor.fetchall()
            conn.close()

        except PermissionError:
            print(
                "[WATCHER] PermissionError reading chat.db. "
                "Run scripts/fda_check.sh and grant Full Disk Access to Terminal "
                "in System Settings → Privacy & Security → Full Disk Access."
            )
            return []
        except sqlite3.OperationalError as e:
            print(f"[WATCHER] Could not open chat.db: {e}")
            return []
        except Exception as e:
            print(f"[WATCHER] Unexpected error reading chat.db: {e}")
            return []

        raw_messages = []
        for row in rows:
            text = row["message"] or ""

            # Skip media-only messages (attachment present, no text body)
            if row["has_attachments"] == 1 and not text.strip():
                print(f"[WATCHER] Skipping media-only message ROWID={row['rowid']}")
                continue

            # Convert Apple timestamp → Unix timestamp.
            # macOS Catalina (10.15)+ stores nanoseconds; earlier versions stored seconds.
            apple_date = row["apple_date"] or 0
            if apple_date > 1_000_000_000_000:   # nanoseconds
                unix_ts = int(apple_date / 1_000_000_000) + APPLE_EPOCH_OFFSET
            else:                                  # seconds (pre-Catalina)
                unix_ts = int(apple_date) + APPLE_EPOCH_OFFSET

            raw_messages.append({
                "id": str(row["rowid"]),   # stable unique ID — no collisions, survives restarts
                "handle": row["handle"],
                "message": text,
                "is_from_me": row["is_from_me"],
                "received_at": unix_ts,
            })

        return self.filter_inbounds(raw_messages)

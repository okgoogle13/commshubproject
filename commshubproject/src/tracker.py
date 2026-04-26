import os
import time
import sqlite3


def _get_conn(db_path, encryption_key):
    """Return a DB connection, using pysqlcipher3 if available, else plain sqlite3."""
    try:
        from pysqlcipher3 import dbapi2 as sqlcipher
        conn = sqlcipher.connect(db_path)
        conn.execute(f"PRAGMA key='{encryption_key}'")
        return conn
    except ImportError:
        return sqlite3.connect(db_path)


class Tracker:
    def __init__(self, db_path=None, encryption_key=None):
        self.db_path = db_path or os.path.expanduser("~/.commshub/state.db")
        self.key = encryption_key or os.environ.get("DB_ENCRYPTION_KEY", "changeme")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _connect(self):
        return _get_conn(self.db_path, self.key)

    def _init_db(self):
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS inbounds (
                message_id TEXT PRIMARY KEY,
                contact_token TEXT NOT NULL,
                imessage_handle TEXT NOT NULL,
                redacted_text TEXT NOT NULL,
                received_at INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at INTEGER NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                message_id TEXT PRIMARY KEY,
                draft_minimal TEXT,
                draft_honest TEXT,
                draft_practical TEXT,
                template_minimal TEXT,
                template_honest TEXT,
                template_practical TEXT,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (message_id) REFERENCES inbounds(message_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                draft_mode TEXT NOT NULL,
                draft_text TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                FOREIGN KEY (message_id) REFERENCES inbounds(message_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS skips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                reason TEXT,
                skipped_at INTEGER NOT NULL,
                FOREIGN KEY (message_id) REFERENCES inbounds(message_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        conn.close()

    def record_inbound(self, message_id, contact_token, imessage_handle, redacted_text, received_at):
        conn = self._connect()
        conn.execute(
            "INSERT OR IGNORE INTO inbounds "
            "(message_id, contact_token, imessage_handle, redacted_text, received_at, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (message_id, contact_token, imessage_handle, redacted_text, received_at, int(time.time())),
        )
        conn.commit()
        conn.close()

    def record_draft(self, message_id, draft_minimal, draft_honest, draft_practical,
                     template_minimal, template_honest, template_practical):
        conn = self._connect()
        conn.execute(
            "INSERT OR REPLACE INTO drafts "
            "(message_id, draft_minimal, draft_honest, draft_practical, "
            "template_minimal, template_honest, template_practical, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (message_id, draft_minimal, draft_honest, draft_practical,
             template_minimal, template_honest, template_practical, int(time.time())),
        )
        conn.execute(
            "UPDATE inbounds SET status='drafted' WHERE message_id=?",
            (message_id,),
        )
        conn.commit()
        conn.close()

    def mark_sent(self, message_id, draft_mode, draft_text, sent_at):
        conn = self._connect()
        conn.execute(
            "INSERT INTO sent (message_id, draft_mode, draft_text, sent_at) VALUES (?, ?, ?, ?)",
            (message_id, draft_mode, draft_text, sent_at),
        )
        conn.execute(
            "UPDATE inbounds SET status='sent' WHERE message_id=?",
            (message_id,),
        )
        conn.commit()
        conn.close()

    def mark_skipped(self, message_id, reason=None):
        conn = self._connect()
        conn.execute(
            "INSERT INTO skips (message_id, reason, skipped_at) VALUES (?, ?, ?)",
            (message_id, reason, int(time.time())),
        )
        conn.execute(
            "UPDATE inbounds SET status='skipped' WHERE message_id=?",
            (message_id,),
        )
        conn.commit()
        conn.close()

    def get_pending_inbounds(self):
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT i.*, d.draft_minimal, d.draft_honest, d.draft_practical, "
            "d.template_minimal, d.template_honest, d.template_practical "
            "FROM inbounds i "
            "LEFT JOIN drafts d ON i.message_id = d.message_id "
            "WHERE i.status IN ('pending', 'drafted') "
            "ORDER BY i.received_at ASC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def days_since_last_sent(self, contact_token):
        conn = self._connect()
        row = conn.execute(
            "SELECT s.sent_at FROM sent s "
            "JOIN inbounds i ON s.message_id = i.message_id "
            "WHERE i.contact_token=? ORDER BY s.sent_at DESC LIMIT 1",
            (contact_token,),
        ).fetchone()
        conn.close()
        if not row:
            return 999
        try:
            last_ts = float(row[0])
            return (time.time() - last_ts) / 86400
        except (ValueError, TypeError):
            return 999

    def is_known_message(self, message_id):
        conn = self._connect()
        row = conn.execute(
            "SELECT 1 FROM inbounds WHERE message_id=?", (message_id,)
        ).fetchone()
        conn.close()
        return row is not None

    def get_status_summary(self):
        conn = self._connect()
        pending = conn.execute(
            "SELECT COUNT(*) FROM inbounds WHERE status IN ('pending', 'drafted')"
        ).fetchone()[0]
        total_sent = conn.execute("SELECT COUNT(*) FROM sent").fetchone()[0]
        last_poll = conn.execute(
            "SELECT value FROM meta WHERE key='last_poll' LIMIT 1"
        ).fetchone()
        conn.close()
        return {
            "pending": pending,
            "total_sent": total_sent,
            "last_poll": last_poll[0] if last_poll else "never",
        }

    def set_last_poll(self, timestamp_str):
        conn = self._connect()
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('last_poll', ?)",
            (timestamp_str,),
        )
        conn.commit()
        conn.close()

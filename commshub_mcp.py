#!/usr/bin/env python3
"""commshub — an MCP stdio server for reading Messages, staging drafts, and sending.

Three pieces make up the whole system:

  1. this file
  2. ~/.config/commshub/roster.json   (0600, never in git — it holds handles)
  3. a Cowork scheduled task that calls pending() then stage()

Approval is deliberately NOT part of the scheduled run: a scheduled session
cannot block waiting for a human. The task drafts and stages, then ends. You
approve later, in any session, via queue() then send().

No third-party imports, by design. A major OS upgrade must not be able to break
this by moving a Python version out from under a virtualenv.

Voice lives nowhere in this file. +COMMS is delivered by paste into a session's
project instructions; code can only embed it (a derived variant) or read it from
a machine-specific path. Neither is permitted. See llm-specs/operations.md.
"""

import json
import os
import sqlite3
import subprocess
import sys
import time

CONFIG_DIR = os.path.expanduser("~/.config/commshub")
ROSTER_PATH = os.path.join(CONFIG_DIR, "roster.json")
QUEUE_PATH = os.path.join(CONFIG_DIR, "queue.json")
CHAT_DB = os.path.expanduser("~/Library/Messages/chat.db")

APPLE_EPOCH = 978307200  # 2001-01-01 in unix seconds
VERIFY_TIMEOUT = 5.0     # seconds to wait for the sent row to appear
VERIFY_POLL = 0.25

ROSTER_SKELETON = {
    "_comment": "0600. Never commit this. One row per conversation, not per person.",
    "rows": [
        {
            "token": "PARENTS",
            "label": "Parents (group thread)",
            "chat_guid": "",
            "handle": "",
            "names": [],
            "reply_grace_hours": 18,
            "initiate_days": 7,
        },
        {
            "token": "FRIEND_1",
            "label": "",
            "chat_guid": "",
            "handle": "",
            "names": [],
            "reply_grace_hours": 24,
            "initiate_days": 21,
        },
        {
            "token": "FRIEND_2",
            "label": "",
            "chat_guid": "",
            "handle": "",
            "names": [],
            "reply_grace_hours": 24,
            "initiate_days": 21,
        },
    ],
}


# --- config -----------------------------------------------------------------

def load_roster():
    """Return (rows, error). A missing roster fails loudly rather than
    returning an empty list — a fresh checkout with no roster must not look
    like a working system with nothing to do."""
    if not os.path.exists(ROSTER_PATH):
        os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
        with open(ROSTER_PATH, "w") as f:
            json.dump(ROSTER_SKELETON, f, indent=2)
        os.chmod(ROSTER_PATH, 0o600)
        return None, {
            "error": "roster_missing",
            "message": f"No roster. Wrote a skeleton to {ROSTER_PATH}.",
            "fix": "Fill in chat_guid (or handle) and names for each row, then retry.",
        }

    with open(ROSTER_PATH) as f:
        rows = json.load(f).get("rows", [])

    live = [r for r in rows if r.get("chat_guid") or r.get("handle")]
    if not live:
        return None, {
            "error": "roster_empty",
            "message": f"{ROSTER_PATH} has no row with a chat_guid or handle.",
            "fix": "Fill in at least one row. Prefer chat_guid — it is the only "
                   "way to address a group thread.",
        }
    return live, None


def find_row(rows, token):
    for r in rows:
        if r["token"] == token:
            return r
    return None


# --- chat.db ----------------------------------------------------------------

def open_db():
    """Return (connection, error). The FDA-absent case is a checkbox, not a
    fault, and must say so — it is the single most likely thing to break after
    a macOS upgrade."""
    if not os.path.exists(CHAT_DB):
        return None, {
            "error": "no_chat_db",
            "message": f"{CHAT_DB} does not exist.",
            "fix": "Sign in to Messages first.",
        }
    try:
        conn = sqlite3.connect(f"file:{CHAT_DB}?mode=ro", uri=True, timeout=5)
        conn.execute("select count(*) from sqlite_master").fetchone()
        return conn, None
    except sqlite3.Error:
        return None, {
            "error": "fda_denied",
            "message": "Can't read your Messages history — Full Disk Access is not granted.",
            "fix": "System Settings -> Privacy & Security -> Full Disk Access. "
                   f"Grant it to the app that runs this server (this process is "
                   f"{sys.executable}, launched by PID {os.getppid()}), then restart it.",
        }


def to_unix(raw):
    if raw is None:
        return 0
    # Modern macOS stores nanoseconds since the Apple epoch; older stored seconds.
    seconds = raw / 1e9 if raw > 1e12 else raw
    return seconds + APPLE_EPOCH


def attributed_text(blob):
    """Pull plain text out of an NSAttributedString typedstream blob.

    macOS 11+ often leaves message.text NULL and puts the body here. This is a
    byte heuristic over an undocumented archive format, so it is allowed to
    fail: it returns None and callers degrade. Nothing load-bearing depends on
    it — send verification matches on chat and timestamp, not on text.
    """
    if not blob:
        return None
    try:
        i = blob.index(b"NSString")
    except ValueError:
        return None
    j = i + 8
    while j < len(blob) and blob[j] in (0x01, 0x02, 0x2B, 0x84, 0x94, 0x95):
        j += 1
    if j >= len(blob):
        return None
    n = blob[j]
    j += 1
    if n == 0x81:
        if j + 2 > len(blob):
            return None
        n = int.from_bytes(blob[j:j + 2], "little")
        j += 2
    try:
        return blob[j:j + n].decode("utf-8")
    except (UnicodeDecodeError, IndexError):
        return None


def chat_filter(row):
    """Return (sql_fragment, params) selecting the row's conversation.

    Always constrains on the *chat*, never on the message's handle. Outbound
    messages carry handle_id 0, so filtering by handle would silently drop
    everything the user sent — which would leave `mine` empty and disable the
    initiate branch entirely, with no error.
    """
    if row.get("chat_guid"):
        return "c.guid = ?", [row["chat_guid"]]
    return (
        "c.ROWID in (select chj.chat_id from chat_handle_join chj "
        "join handle h on h.ROWID = chj.handle_id where h.id = ?)",
        [row["handle"]],
    )


def recent_messages(conn, row, limit=12):
    where, params = chat_filter(row)
    sql = f"""
        select m.text, m.attributedBody, m.date, m.is_from_me
        from message m
        join chat_message_join cmj on cmj.message_id = m.ROWID
        join chat c on c.ROWID = cmj.chat_id
        where {where}
        order by m.date desc
        limit ?
    """
    out = []
    for text, blob, date, is_from_me in conn.execute(sql, params + [limit]):
        out.append({
            "text": text or attributed_text(blob),
            "at": to_unix(date),
            "from_me": bool(is_from_me),
        })
    return out


# --- the encoding layer -----------------------------------------------------

def deidentify(text, rows):
    """Replace every known name and handle with its row token.

    This is the reason the daemon exists. A model drafting a reply needs the
    conversation's content but must never receive a handle: a handle is
    contactability, and it is not the user's to disclose on someone else's
    behalf. The reverse direction lives in send(), and the map never leaves
    this process.
    """
    if not text:
        return text
    pairs = []
    for r in rows:
        for name in r.get("names", []):
            pairs.append((name, r["token"]))
        if r.get("handle"):
            pairs.append((r["handle"], r["token"]))
    # Longest first, so "Anna Marie" is not half-replaced by "Anna".
    for needle, token in sorted(pairs, key=lambda p: -len(p[0])):
        if needle:
            text = text.replace(needle, token)
    return text


# --- tools ------------------------------------------------------------------

def tool_pending():
    """Which conversations need attention, and why.

    Deliberately does NOT use read state. Opening Messages marks a thread read,
    and reading-without-replying is exactly the avoidance this system exists to
    catch — keying on unread would make it go quiet when it matters most.
    """
    rows, err = load_roster()
    if err:
        return err
    conn, err = open_db()
    if err:
        return err

    now = time.time()
    out = []
    with conn:
        for row in rows:
            msgs = recent_messages(conn, row)
            if not msgs:
                continue
            last = msgs[0]
            mine = next((m for m in msgs if m["from_me"]), None)

            branch = None
            if not last["from_me"]:
                if now - last["at"] > row.get("reply_grace_hours", 24) * 3600:
                    branch = "reply"
            elif mine and now - mine["at"] > row.get("initiate_days", 21) * 86400:
                branch = "initiate"
            if not branch:
                continue

            out.append({
                "row": row["token"],
                "label": row.get("label") or row["token"],
                "branch": branch,
                "days_since_my_last": round((now - mine["at"]) / 86400, 1) if mine else None,
                "context": [
                    {
                        "from_me": m["from_me"],
                        "days_ago": round((now - m["at"]) / 86400, 1),
                        "text": deidentify(m["text"], rows),
                    }
                    for m in reversed(msgs[:6])
                ],
            })
    conn.close()
    return {"pending": out}


def read_queue():
    if not os.path.exists(QUEUE_PATH):
        return []
    with open(QUEUE_PATH) as f:
        return json.load(f).get("staged", [])


def write_queue(staged):
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
    with open(QUEUE_PATH, "w") as f:
        json.dump({"staged": staged}, f, indent=2)
    os.chmod(QUEUE_PATH, 0o600)


def tool_stage(row_token, drafts):
    rows, err = load_roster()
    if err:
        return err
    if not find_row(rows, row_token):
        return {"error": "unknown_row", "message": f"No roster row named {row_token}."}

    staged = [s for s in read_queue() if s["row"] != row_token]
    staged.append({"row": row_token, "drafts": drafts, "staged_at": time.time()})
    write_queue(staged)
    return {"staged": row_token, "count": len(drafts)}


def tool_queue():
    """Staged drafts awaiting approval, freshest first.

    Drops anything past its row's initiate threshold. A draft referencing a
    five-day-old message is worse than no draft — it reads as inattention
    rather than as contact.
    """
    rows, err = load_roster()
    if err:
        return err

    now = time.time()
    live, dropped = [], 0
    for s in read_queue():
        row = find_row(rows, s["row"])
        max_age = (row.get("initiate_days", 21) if row else 21) * 86400
        if now - s["staged_at"] > max_age:
            dropped += 1
            continue
        s["age_hours"] = round((now - s["staged_at"]) / 3600, 1)
        live.append(s)

    if dropped:
        write_queue(live)
    live.sort(key=lambda s: -s["staged_at"])
    return {"staged": live, "dropped_stale": dropped}


def tool_send(row_token, text):
    """Re-identify, send via Messages, then verify the row actually landed.

    The verification is the point. Without it the failure mode is a success
    banner over a message that never arrived, and the only thing that would
    ever surface it is the recipient saying they haven't heard from you —
    which is the exact outcome this system exists to prevent.
    """
    rows, err = load_roster()
    if err:
        return err
    row = find_row(rows, row_token)
    if not row:
        return {"error": "unknown_row", "message": f"No roster row named {row_token}."}

    conn, db_err = open_db()
    started = time.time()

    if row.get("chat_guid"):
        script = 'on run argv\ntell application "Messages" to send (item 2 of argv) to chat id (item 1 of argv)\nend run'
        target = row["chat_guid"]
    else:
        script = ('on run argv\ntell application "Messages"\n'
                  'set svc to 1st service whose service type = iMessage\n'
                  'send (item 2 of argv) to buddy (item 1 of argv) of svc\n'
                  'end tell\nend run')
        target = row["handle"]

    # Text goes through argv, never through string interpolation into the script.
    proc = subprocess.run(
        ["osascript", "-e", script, target, text],
        capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        if conn:
            conn.close()
        stderr = proc.stderr.strip()
        # A permission refusal and a bad target both exit non-zero. Collapsing
        # them into one message is the failure this design exists to avoid: one
        # is a checkbox, the other is a stale roster.
        denied = "-1743" in stderr or "not authori" in stderr.lower()
        if denied:
            return {
                "sent": False, "verified": False, "error": "automation_denied",
                "message": f"Messages refused the send: {stderr}",
                "fix": "System Settings -> Privacy & Security -> Automation. Allow the "
                       "app running this server to control Messages.",
            }
        return {
            "sent": False, "verified": False, "error": "send_failed",
            "message": f"Messages accepted the request but the send failed: {stderr}",
            "fix": f"Usually a stale target. Check chat_guid/handle for {row_token} "
                   f"in {ROSTER_PATH}.",
        }

    if db_err:
        return {
            "sent": True,
            "verified": False,
            "error": db_err["error"],
            "message": "Sent, but can't verify it arrived — " + db_err["message"],
            "fix": db_err["fix"],
        }

    # Verify: a new outbound row in this conversation, dated after we started.
    where, params = chat_filter(row)
    sql = f"""
        select count(*) from message m
        join chat_message_join cmj on cmj.message_id = m.ROWID
        join chat c on c.ROWID = cmj.chat_id
        left join handle h on h.ROWID = m.handle_id
        where {where} and m.is_from_me = 1 and m.date > ?
    """
    threshold = int((started - APPLE_EPOCH) * 1e9)
    deadline = time.time() + VERIFY_TIMEOUT
    verified = False
    while time.time() < deadline:
        if conn.execute(sql, params + [threshold]).fetchone()[0] > 0:
            verified = True
            break
        time.sleep(VERIFY_POLL)
    conn.close()

    if verified:
        write_queue([s for s in read_queue() if s["row"] != row_token])
        return {"sent": True, "verified": True, "row": row_token}

    return {
        "sent": True,
        "verified": False,
        "error": "not_delivered",
        "message": f"Sent, but no matching message appeared in the thread within "
                   f"{VERIFY_TIMEOUT:.0f}s. This is a delivery problem, not a settings one.",
        "fix": "Open the thread and check. If it isn't there, the handle or chat_guid "
               "in your roster may be stale.",
    }


# --- MCP stdio --------------------------------------------------------------

TOOLS = [
    {
        "name": "pending",
        "description": "Conversations needing a reply or an initiate, with de-identified "
                       "context. Returns row tokens, never handles or real names.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "stage",
        "description": "Store drafts for a row, awaiting approval in a later session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "row": {"type": "string", "description": "Row token, e.g. PARENTS"},
                "drafts": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["row", "drafts"],
        },
    },
    {
        "name": "queue",
        "description": "Staged drafts awaiting approval. Stale ones are dropped.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "send",
        "description": "Send text to a row and verify it landed. Returns verified:false "
                       "with a specific fix when it did not.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "row": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["row", "text"],
        },
    },
]


def dispatch(name, args):
    if name == "pending":
        return tool_pending()
    if name == "stage":
        return tool_stage(args["row"], args["drafts"])
    if name == "queue":
        return tool_queue()
    if name == "send":
        return tool_send(args["row"], args["text"])
    return {"error": "unknown_tool", "message": name}


def list_threads(days=30):
    """Print every conversation touched recently, as ready-to-paste roster rows.

    Deliberately NOT an MCP tool. Its whole output is handles and display names,
    and an MCP tool's return value lands in whatever session called it — which
    is the exact disclosure this server exists to prevent. Setup is the one step
    that legitimately needs handles, so it runs in a terminal where no model is
    in the loop: read it, paste it into the roster, done.

    Also the only way to exercise the read half without sending anything.
    """
    conn, err = open_db()
    if err:
        print(f"{err['message']}\n\n{err['fix']}", file=sys.stderr)
        return 1

    cutoff = int((time.time() - days * 86400 - APPLE_EPOCH) * 1e9)
    rows = conn.execute("""
        select c.ROWID, c.guid, c.display_name, max(m.date) as last_date
        from chat c
        join chat_message_join cmj on cmj.chat_id = c.ROWID
        join message m on m.ROWID = cmj.message_id
        group by c.ROWID
        having max(m.date) > ?
        order by last_date desc
    """, [cutoff]).fetchall()

    print(f"# {len(rows)} conversation(s) touched in the last {days} days.")
    print(f"# Paste the ones you want into {ROSTER_PATH}.\n")
    n_1to1 = 0
    for i, (rowid, guid, display, last_date) in enumerate(rows, 1):
        handles = [h for (h,) in conn.execute(
            "select h.id from chat_handle_join chj join handle h on h.ROWID = chj.handle_id "
            "where chj.chat_id = ?", [rowid])]
        age = (time.time() - to_unix(last_date)) / 86400
        kind = "group" if len(handles) > 1 else "1:1"
        if kind == "1:1":
            n_1to1 += 1
        label = display or (handles[0] if handles else "?")
        print(f"[{i}] {label}  "
              f"({kind}, {len(handles)} participant(s), last {age:.1f}d ago)")
        print(json.dumps({
            "token": "PARENTS" if kind == "group" else f"FRIEND_{n_1to1}",
            "label": display or "",
            "chat_guid": guid,
            "handle": "" if kind == "group" else (handles[0] if handles else ""),
            "names": [],
            "reply_grace_hours": 18 if kind == "group" else 24,
            "initiate_days": 7 if kind == "group" else 21,
        }, indent=2))
        print()
    conn.close()
    print("# Fill in 'names' with the display names used in these threads —")
    print("# that is what lets the server strip them before a model sees anything.")
    return 0


def reply(msg_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        method, msg_id = msg.get("method"), msg.get("id")
        if msg_id is None:
            continue  # a notification; nothing to answer

        if method == "initialize":
            reply(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "commshub", "version": "1.0.0"},
            })
        elif method == "tools/list":
            reply(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = msg.get("params", {})
            result = dispatch(params.get("name"), params.get("arguments") or {})
            reply(msg_id, {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "structuredContent": result,
            })
        else:
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": f"unknown method {method}"},
            }) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if "--threads" in sys.argv:
        n = sys.argv[sys.argv.index("--threads") + 1] if len(sys.argv) > sys.argv.index("--threads") + 1 else "30"
        sys.exit(list_threads(int(n)))
    main()

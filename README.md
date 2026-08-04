# commshub

Sends one message on a bad day, and tells you if it didn't arrive.

## The three pieces

1. **`commshub_mcp.py`** — an MCP stdio server. Stdlib only, no venv, no dependencies.
   Four tools: `pending`, `stage`, `queue`, `send`.
2. **`~/.config/commshub/roster.json`** — 0600, outside this repo, never in git.
   One row per *conversation*, not per person, so the parents' group thread is one row.
   Holds handles and per-row thresholds. The server writes a skeleton on first run and
   refuses to do anything until you fill it in.
3. **A Cowork scheduled task** — every 2 days. Calls `pending()`, drafts under +COMMS,
   calls `stage()`, ends. It does not wait for you; a scheduled session can't block.

You approve later, in any session: ask for the queue, pick one, send.

## Setup, in order

```bash
python3 commshub_mcp.py --threads 30
```

Prints every conversation touched in the last 30 days as a ready-to-paste roster row —
`chat_guid`, participants, how long since anyone spoke. Copy the ones you want into
`~/.config/commshub/roster.json` and fill in `names`.

**`--threads` is deliberately not an MCP tool.** Its entire output is handles and display
names, and an MCP tool's return value lands in whatever session called it — the exact
disclosure this server exists to prevent. Setup is the one step that legitimately needs
handles, so it runs in a terminal with no model in the loop. It is also the only way to
exercise the read half without sending anything.

Then: grant Full Disk Access → run `pending` → send once to a throwaway thread → only
then rely on it.

## Wiring

Register the server with your MCP client:

```json
{ "commshub": { "command": "/usr/bin/python3", "args": ["<repo>/commshub_mcp.py"] } }
```

The scheduled task's prompt should say: call `pending`; for each row draft three
genuinely different angles; call `stage`. **It must not send.**

## Two permissions, and they will break

Both are TCC grants, and TCC is the most common casualty of a major macOS upgrade.

- **Full Disk Access** — to read `~/Library/Messages/chat.db`. Without it, `pending`
  returns nothing useful and sends report `verified: false`.
- **Automation → Messages** — to send. Without it, `send` returns `automation_denied`.

Grant both to the *app that launches the server*, not to `python3`. System Settings →
Privacy & Security. Every error from this server names which one it needs and where.

## Why there is no voice config here

+COMMS can only be delivered by paste. Code can embed it (a derived variant, which
drifts) or read it from a path (machine-specific). Neither is allowed, so drafting
happens in a session that already carries +COMMS in its project instructions, and this
repo defines no tone, personas, or output schema. See `llm-specs/operations.md`.

## Verification is the point

`send` doesn't trust `osascript`. It records a timestamp, sends, then polls `chat.db`
for a new outbound row in that conversation. Without that check the failure mode is a
success banner over a message that never arrived — and the only thing that would ever
surface it is the recipient saying they haven't heard from you, which is the outcome
this exists to prevent.

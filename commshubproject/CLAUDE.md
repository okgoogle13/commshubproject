# Comms Hub — CLAUDE.md

Personal macOS Python CLI. Reads iMessage conversations, drafts replies via Gemini AI,
surfaces them in an interactive terminal digest. Operator approves every send. No automation.

---

## Project roots

| Path | Purpose |
|------|---------|
| `/Users/okgoogle13/Projects/commshubproject/commshubproject` | Python CLI root (work from here) |
| `src/` | Core modules |
| `tests/` | Pytest suite |
| `config/` | YAML/JSON config — allow_list, schedule, exemplars, voice rules |
| `commshub_bridge.py` | FastAPI HTTP bridge for the send-one-message web artifact |
| `bridge-workflow.md` | Staged build plan for the bridge (reference before editing bridge) |
| `venv/` | Local virtualenv — always activate before running anything |

---

## Activation

```bash
cd /Users/okgoogle13/Projects/commshubproject/commshubproject
source venv/bin/activate
```

---

## Key commands

```bash
# Check Full Disk Access (required for chat.db reads)
bash scripts/fda_check.sh

# Poll iMessage for new inbounds, draft replies
python -m src.cli watch

# Interactive digest — review drafts, approve sends
python -m src.cli digest

# Show pending count and last poll time
python -m src.cli status

# Test redactor + drafter + linter without a real inbound
python -m src.cli --test-draft "some text here"

# Run full test suite
python -m pytest tests/ -v

# Start the HTTP bridge (required for web artifact Send button)
uvicorn commshub_bridge:app --host 127.0.0.1 --port 8765
```

---

## Architecture

```
iMessage chat.db
      ↓
  watcher.py       — polls chat.db, filters to allow-listed contacts
      ↓
  redactor.py      — strips PII before anything leaves the machine
      ↓
  drafter.py       — calls Gemini, returns 3 variants: minimal / honest / practical_reentry
      ↓
  tracker.py       — SQLite: records inbounds, drafts, sends, silence durations
      ↓
  digest.py        — interactive TUI: operator reviews drafts, picks one, confirms
      ↓
  sender.py        — AppleScript → Messages.app → real iMessage send
      ↑
commshub_bridge.py — FastAPI wrapper around sender._send_via_applescript
                     used by send-one-message.html artifact via POST /send-message
```

---

## Allow-listed contacts

Defined in two places — **keep in sync**:

| File | Location |
|------|----------|
| `config/allow_list.yaml` | Source of truth for CLI pipeline |
| `commshub_bridge.py` → `ALLOW_LIST` | Must mirror allow_list.yaml |

**Current contacts:**

| Token | Name | iMessage handle |
|-------|------|----------------|
| MUM | Molly Dougall | molly.dougall@icloud.com |
| DAD | Arvind Dougall | drarvinddougall@gmail.com |
| LUCY | Lucy Gunner | gunner.lucy@gmail.com |

Operator handle: `jonas.dougall@icloud.com` (Melbourne, Australia/Melbourne)

---

## Hard constraints

- **Full Disk Access required** — watcher.py reads `~/Library/Messages/chat.db` directly. Without FDA, all polls return zero messages silently.
- **Operator approves every send** — digest.py requires explicit confirmation. There is no auto-send path.
- **Redaction before AI** — redactor.py runs before drafter.py. Raw message text never reaches Gemini.
- **Allow-list is the security gate** — commshub_bridge.py rejects any handle not in ALLOW_LIST, regardless of what the artifact sends.
- **iMessage only** — WhatsApp has no macOS automation API. Deferred indefinitely.

---

## Known gaps

- Group thread sending not implemented (picker in web artifact is honest about this)
- `--send` flag removed from cli.py — direct send routes through digest or bridge only
- Reactive pipeline (watcher → digest → send) requires an inbound to exist; initiation uses the web artifact + bridge directly

---

## Environment

`.env` (at project root) must contain:

```
GEMINI_API_KEY=...
```

Also loaded from `~/.commshub/.env` if present (takes lower precedence).

---

## Proactive workflow rule

When working on this project, Claude must follow this pattern within any approved task:

1. **Work autonomously** to completion within the current approved scope — do not pause for check-ins mid-task unless a decision point arises that was not covered by the instructions.
2. **After completing each step**, always state:
   - What was just done and whether it succeeded
   - What the next planned step is and **why it comes next** (dependency, verification gate, risk order)
   - Whether that next step is **safe to proceed automatically** or **requires confirmation** before starting
3. **Never end passively** (e.g. "Let me know if you'd like me to continue") unless the entire workflow is complete. A partial result is not a stopping point — it is a handoff prompt.
4. **Confirmation is required before** any step that: writes to production, sends a real message, modifies launchd agents, or deletes data.
5. **Workflow complete** means: the original goal is met, verified, and the operator has been told what the system can now do that it could not before.

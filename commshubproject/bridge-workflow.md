# Comms Hub Bridge Workflow

## Before you start

- The HTML artifact may fail inside sandboxed iframes even when the bridge works locally.
- After the bridge is verified, test `send-one-message.html` in a normal local browser context and use its Recheck/Send flow there.
- Use the absolute file path for this workflow file when instructing Claude Code:
  `/Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md`
- Use the latest repomix file as a repo context source when starting any step:
  `/Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml`
- Treat the repomix file as read-only context only. Do not edit it. Make changes in the original repository files.

## Purpose

This file is the single source of truth for planning, building, verifying, and optionally operationalising the local bridge that allows the Comms Hub artifact to trigger message sending through a local HTTP API.

The workflow is designed to reduce drift, force verification, and stop the agent from confusing architecture intent with working implementation.

## Framework rules

- Use sequential thinking.
- Follow four phases unless the step explicitly uses a different label: Inspect, Plan, Implement, Verify.
- Separate planning from implementation.
- Separate dependency present from working implementation.
- Separate scaffold written from runtime verified.
- Never mark a step complete without a verification section.
- If a key assumption is unverified, stop and report it clearly.
- Prefer the smallest working change over architectural expansion.
- Do not claim the bridge works unless the relevant runtime checks have passed.
- Do not send a real message unless the step explicitly authorises a live send.

## Status meanings

- `blocked`
- `implemented-not-running`
- `running-and-verified`
- `tests-written-not-passing`
- `tests-passing`
- `bridge-ok-send-unconfirmed`
- `real-send-confirmed`
- `persistent-bridge-running`
- `verification-incomplete`

## How to use this file

Use one step at a time.

Recommended operator instructions to Claude Code:

- "Read `/Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md` and `/Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml`, then execute Step 1 only. Follow the framework rules exactly. Stop after the verification section and report status."
- "Read `/Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md` and `/Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml`, then execute Step 2 only. Stop after verification."
- "Read `/Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md` and `/Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml`, then execute Step 3 only if Step 1 and Step 2 are fully verified."
- "Read `/Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md` and `/Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml`, then execute Step 4 only if the bridge is already confirmed working."

## Step 1 — Plan before building

```text
You are working in this repo:

/Users/okgoogle13/Projects/commshubproject/commshubproject

Set your working directory to:
/Users/okgoogle13/Projects/commshubproject/commshubproject
Do not infer it from context.

Use a structured workflow with four phases:
1. Inspect
2. Plan
3. Implement
4. Verify

Do not skip phases. Do not start coding until the Plan phase is complete. Do not claim completion until the Verify phase is complete.

Goal:
Build the missing local bridge server that allows the Comms Hub artifact to trigger a real send action via a local HTTP API.

Phase 1 — Inspect
Read and inspect:
- /Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml
- src/sender.py
- requirements.txt
- any existing tests
- any files referencing 8765, /health, /send-message, FastAPI, uvicorn, flask, express, or HTTP server code

Use the repomix file first to understand current repo structure and likely backend-relevant files.
Then verify all important assumptions against the actual source files before coding.
Do not edit the repomix file.

In this phase, determine:
- what the repomix file says about current repo structure and backend-relevant files
- whether _send_via_applescript exists
- its exact function signature
- whether any backend already exists
- whether any test framework already exists

Phase 2 — Plan
Before writing code, produce a short implementation plan with:
- files to create or modify
- dependencies to install, if any
- exact API contract for:
  - GET /health
  - POST /send-message
- validation rules
- how the route will call the sender logic
- risks or uncertainties found during inspection

Stop after the plan and wait for internal confirmation from your own inspection. If a key assumption is unverified, state it clearly before proceeding.

Phase 3 — Implement
Create:
- ./commshub_bridge.py

Requirements:
- FastAPI app
- CORS enabled, allow all origins for local artifact use
- GET /health -> {"ok": true}
- POST /send-message accepts:
  {"recipient": str, "handle": str, "message": str, "mode": str}
- Validate:
  - handle present
  - message non-empty after trim
  - handle in allow-list:
    {"molly.dougall@icloud.com", "drarvinddougall@gmail.com"}
- If valid, call the confirmed sender function from src.sender
- Return:
  - success: {"ok": true}
  - failure: {"ok": false, "error": "clear reason"}

Install fastapi and uvicorn into ./venv only if missing.

Phase 4 — Verify
You must verify all of the following before claiming success:
- the file was created successfully
- imports resolve
- the server starts
- the process listens on 127.0.0.1:8765
- GET /health returns {"ok": true}
- no real message is sent during this step

Completion rules
Explicitly report these statuses separately:
- dependency present
- scaffold implemented
- server running
- live send untested

Output format:
1. Inspection findings
2. Plan
3. Files changed
4. Commands run
5. Verification results
6. Final status: blocked / implemented-not-running / running-and-verified
```

## Step 2 — Safe verification

```text
Now move to structured verification.

Before doing anything, confirm Step 1 status is running-and-verified.
If it is not, stop immediately and report the actual status.
Do not proceed.

Use the same four phases:
1. Inspect
2. Plan
3. Implement
4. Verify

Goal:
Prove the bridge works without sending a real iMessage.

Phase 1 — Inspect
Read:
- /Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml
- src/sender.py
- commshub_bridge.py
- any existing test config or test folders

Use repomix as context for file discovery, but verify tests and runtime assumptions against the real files.
Do not edit the repomix file.

Confirm:
- exact sender callable used by the bridge
- whether pytest is already installed
- whether FastAPI TestClient or requests/httpx is available

Phase 2 — Plan
Produce a concise test plan covering:
- success case with valid allow-listed handle
- failure case with non-allow-listed handle
- failure case with empty message
- failure case with missing/null handle
- mocking strategy so no real AppleScript send occurs

Phase 3 — Implement
Create:
- tests/test_bridge.py

Requirements:
- patch/mock the sender call so no real message is sent
- test the bridge either with FastAPI TestClient or against the local server
- verify JSON responses exactly
- keep tests small and readable

Phase 4 — Verify
Run the tests and verify:
- mock was used
- no real send occurred
- valid handle returns {"ok": true}
- invalid handle returns {"ok": false}
- empty or missing fields return {"ok": false}
- tests pass cleanly

Completion rules
Do not claim success unless tests pass.

Output format:
1. Inspection findings
2. Test plan
3. Files changed
4. Commands run
5. Test results
6. Final status: blocked / tests-written-not-passing / tests-passing
```

## Step 3 — Controlled real-world execution

```text
⚠️ This step will send a real iMessage. Do not proceed unless Step 2 is tests-passing.

Only run this if Step 1 is verified and Step 2 tests are passing.

Use a structured workflow:
1. Pre-flight
2. Execute
3. Observe
4. Verify

Goal:
Run one controlled real send through the local bridge.

Phase 1 — Pre-flight
Before sending anything:
- re-read /Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml for repo context if needed, but treat runtime checks and real files as authoritative
- confirm the server is running
- confirm /health returns {"ok": true}
- restate clearly that this step may send a real iMessage
- confirm the payload matches the actual API contract

Phase 2 — Execute
Send this payload to the local bridge:

POST http://127.0.0.1:8765/send-message
{
  "recipient": "mum",
  "handle": "molly.dougall@icloud.com",
  "message": "Test from Comms Hub — ignore this.",
  "mode": "initiate"
}

Use curl or httpx.

Phase 3 — Observe
Capture:
- exact request command
- exact HTTP response
- any server log output if relevant

Phase 4 — Verify
Confirm separately:
- whether the HTTP request succeeded
- whether the sender function ran
- whether Messages.app appears to have sent the message
- whether any failure came from bridge logic, permissions, AppleScript, or environment

Completion rules
Do not say “working” unless both the HTTP response and actual observed send are confirmed.

Output format:
1. Pre-flight checks
2. Request command
3. Response
4. Observed outcome
5. Verification
6. Final status: failed / bridge-ok-send-unconfirmed / real-send-confirmed
```

## Step 4 — Persistence and operationalisation

```text
Only run this if the bridge has been verified as working.

Use a structured workflow:
1. Inspect
2. Plan
3. Implement
4. Verify

Goal:
Make the local bridge survive login/reboot with minimal manual effort.

Phase 1 — Inspect
Confirm:
- current working server command
- correct venv uvicorn path
- preferred log path exists or can be created
- re-check repomix-output.xml for any existing launchd/persistence-related files or conflicting operational setup

Phase 2 — Plan
Summarise the launchd setup:
- plist path
- working directory
- command
- log destination
- expected verification steps

Phase 3 — Implement
Create:
~/Library/LaunchAgents/com.commshub.bridge.plist

Requirements:
- command:
  /Users/okgoogle13/Projects/commshubproject/commshubproject/venv/bin/uvicorn commshub_bridge:app --host 127.0.0.1 --port 8765
- working directory:
  /Users/okgoogle13/Projects/commshubproject/commshubproject
- stdout/stderr:
  ~/Library/Logs/commshub_bridge.log
- RunAtLoad = true
- KeepAlive = true

Load it with launchctl.

Phase 4 — Verify
Verify:
- plist written successfully
- launchctl load/bootstrap command succeeded
- process is running
- GET /health returns {"ok": true}
- logs show no immediate crash loop

Completion rules
Do not claim persistence is working without both process evidence and successful health check.

Output format:
1. Inspection findings
2. Plan
3. Files changed
4. Commands run
5. Verification results
6. Final status: blocked / configured-not-running / persistent-bridge-running
```

## Optional wrapper prompts

### Wrapper for Step 1

```text
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml
Then execute Step 1 only.

Use the repomix file for repo context and file discovery.
Verify all important assumptions against the real files before coding.
Do not edit the repomix file.
Follow the framework rules exactly.
Stop after the verification section and report status.
```

### Wrapper for Step 2

```text
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml
Then execute Step 2 only.

Use the repomix file for repo context and file discovery.
Verify all important assumptions against the real files before testing.
Do not edit the repomix file.

Before doing anything, confirm Step 1 status is running-and-verified.
If it is not, stop immediately and report the actual status.
Do not proceed.
Stop after the verification section and report status.
```

### Wrapper for Step 3

```text
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml
Then execute Step 3 only.

Use the repomix file for repo context only.
Do not edit the repomix file.
⚠️ This step will send a real iMessage. Do not proceed unless Step 2 is tests-passing.
Only proceed if Step 1 is running-and-verified and Step 2 is tests-passing.
Stop after the verification section and report status.
```

### Wrapper for Step 4

```text
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/bridge-workflow.md
Read /Users/okgoogle13/Projects/commshubproject/commshubproject/repomix-output.xml
Then execute Step 4 only.

Use the repomix file for repo context and discovery of any existing persistence setup.
Verify against the real files before making changes.
Do not edit the repomix file.
Only proceed if the bridge is already confirmed working.
Stop after the verification section and report status.
```

## Final note

This workflow file and the latest repomix file should always be referenced by absolute path when used from Claude Code.

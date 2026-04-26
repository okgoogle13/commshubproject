# COMMS HUB — Google AI Studio Build Prompt
# Paste this entire document into AI Studio "Build App" mode with Gemini 2.5 Pro

---

## YOUR TASK

Build a macOS Python application called **Comms Hub**. It is a family-comms agent that reads iMessage conversations hourly, drafts replies using Gemini 2.5 Pro, and surfaces those drafts in a 4x-daily digest so the operator can send each reply with a single terminal command. No GUI required. CLI-first.

Build Milestone 1 only. Stop after Milestone 1 is complete and verified.

---

## OPERATOR CONTEXT

The operator is a neurodivergent adult in Melbourne, Australia. They experience communication paralysis — high-stakes family message threads go unanswered for days or weeks not from lack of love but from executive function failure. The system's job is to remove every friction point except the final send decision.

**Non-negotiables:**
- Every send requires explicit operator approval. No exceptions.
- No message is ever sent automatically.
- No inbound content leaves the machine without passing through the redactor first.
- System fails closed: if drafting fails, the digest still fires and flags the item as "draft unavailable."

---

## OPERATOR CONFIG

```yaml
operator:
  imessage_handle: jonas.dougall@icloud.com
  timezone: Australia/Melbourne
  install_path: /Users/okgoogle13/Projects/commshubproject

allow_list:
  - name: Molly Dougall
    imessage_handle: molly.dougall@icloud.com
    role: mother
    voice_notes: true
    primary_channel: iMessage
  - name: Daddy Dougall
    imessage_handle: drarvindougall@gmail.com
    role: father
    primary_channel: iMessage

digest:
  times: ["09:00", "13:00", "18:00", "21:00"]
  timezone: Australia/Melbourne

watcher:
  poll_interval_minutes: 60

gemini:
  model: gemini-2.5-pro-preview-03-25
  temperature_primary: 0.7
  temperature_alternative: 1.1
  api_key: ${GEMINI_API_KEY}
```

---

## VOICE RULES

The drafter must match these rules exactly. These are non-negotiable style constraints baked into every system prompt call.

```
VOICE RULES — apply to every draft without exception:

1. Write like a tired, loving adult child texting their parents from Melbourne.
2. Never use formal openers: no "I hope this finds you well", no "Dear Mum and Dad".
3. Never use formal sign-offs: no "Warm regards", no "Best".
4. Use "xx" at the end. Always.
5. Use "🙈" sparingly for self-deprecating moments. No other emoji unless in a template.
6. Never explain ADHD or neurodivergence directly to parents.
7. Never promise a specific call time unless the operator has confirmed it.
8. Never apologise more than once per message.
9. Match the energy level of the selected template: Zero / Low / Medium.
10. Prefer short. Under 60 words for Zero/Low energy. Under 100 words for Medium.
11. When filling in a Reply Bridge template, replace [insert X] placeholders with context from the inbound message where available, or leave a [FILL IN] marker for the operator to complete.
```

---

## VOICE EXEMPLARS

These are real messages sent by the operator. Match this voice exactly.

```
EXEMPLAR 1 (re-entry, medium energy):
"Hi Mum & Dad 💕 Miss you and sorry about my poor conduct lately 🙈 Been struggling for a few months, actually, ever since you left !! But today I'm feeling better enough to look at my phone and send you a message, which is a relief and progress ✨ Maybe we can talk tomorrow? How are u? When's the next London trip, & have you decided on India? ✈️ Love you xx"

EXEMPLAR 2 (practical, low energy):
"Hi parents. Let me know when you are free to talk. Maybe after you've had lunch UK time? Let me know if that works and I'll call. xx"

EXEMPLAR 3 (reset, medium energy):
"I know it's been ages. Brain's been a bit frozen, not my love for you. Thinking of you both xx"

EXEMPLAR 4 (minimal, zero energy):
"Hi — am ok, just very in my head lately. Love you both xx"

EXEMPLAR 5 (time blindness, low energy):
"I saw this message arrive and then it was somehow three weeks later. I am genuinely not sure what happened. Love you both xx"
```

---

## REPLY BRIDGE TEMPLATES

These 77 templates are the primary drafting resource. The drafter must select the best-matching template first, then adapt it to context. Freeform generation is a fallback only when no template fits.

```csv
ID,Category,Goal_Intent,Energy_Level,Message_Template
RB-001,The Classic Reset,Honest Reset,Medium,"Hi parents. Sorry for the silence lately. I've been feeling pretty low and literally have no updates, which is a bit embarrassing. But I think about you both every day. Will try calling tomorrow. Love you both xx"
RB-002,The Classic Reset,Honest Reset,Medium,"I know it's been ages. Brain's been a bit frozen, not my love for you. Thinking of you both xx"
RB-003,The Classic Reset,Honest Reset,Medium,"Parents! Sorry for dropping off the radar. Brain hit a wall. I don't have any proper news but I love you both and I'm okay. Let's chat this weekend? xx"
RB-004,Time Blindness and Glitches,Acknowledge Delay,Low,"Hi parents! I replied to this in my head three days ago and just realised I never actually typed it out. Brain glitch! Love you both xx"
RB-005,Time Blindness and Glitches,Acknowledge Delay,Low,"Wow, time completely got away from me this week. Still alive! Just deeply disorganized 🙈 Love you guys xx"
RB-006,Time Blindness and Glitches,Acknowledge Delay,Low,"Sorry for the delay, I got totally distracted and lost track of time. Hope you're both doing well! xx"
RB-007,Time Blindness and Glitches,Acknowledge Delay,Low,"I opened this message, got distracted by something shiny, and forgot to reply. I'm the worst, but I love you! xx"
RB-008,Minimal Alive Signals,Buy Time / Reassure,Zero,"Hi — am ok, just very in my head lately. Love you both xx"
RB-009,Minimal Alive Signals,Buy Time / Reassure,Zero,"Social battery is at 1% today, but wanted to send a quick wave. 👋 Love you both! xx"
RB-010,Minimal Alive Signals,Buy Time / Reassure,Zero,"Very quiet brain day today. Just sending some love your way. xx"
RB-011,Minimal Alive Signals,Buy Time / Reassure,Zero,"Not ignoring you, just operating at a snail's pace today. Will catch up properly soon! xx"
RB-012,Minimal Alive Signals,Buy Time / Reassure,Zero,"Just a quick ping to say I'm alive and safe, just hiding from my inbox. Love you guys. xx"
RB-013,Missed Call Recovery,Reset Connection,Low,"Sorry I missed your attempts to call me back. Brain was a bit fried. Will try again tomorrow. Love you xx"
RB-014,Missed Call Recovery,Reset Connection,Low,"Hi parents sorry I didn't call today. Total disaster re: meds. I'm still so sleepy. Will call you tomorrow xx"
RB-015,Missed Call Recovery,Reset Connection,Low,"Sorry I didn't call. Am grumpy. Will call tomorrow x"
RB-016,Missed Call Recovery,Reset Connection,Low,"Whoops sorry was watching a movie. What time should I try calling tomorrow?"
RB-017,Admin and Life Disasters,Explain Stressor,Low,"Slight disaster part 2: [insert minor inconvenience]. Why am I like this 🙈 Will call when I sort it out! xx"
RB-018,Admin and Life Disasters,Explain Stressor,Low,"Just spent an hour trying to fix [insert tech/admin thing]. Brain is now mush. Speak tomorrow! xx"
RB-019,Admin and Life Disasters,Explain Stressor,Low,"Total disaster today with [insert thing]. I'm exhausted. Hope you guys had a better day than me! xx"
RB-020,Random Hyperfocus,Warm Deflect,Medium,"Dad, random question... how much rent would a tenant pay for [insert place]? Hypothetically"
RB-021,Random Hyperfocus,Warm Deflect,Medium,"Mum, you will not believe the price of [insert item] at the supermarket today. Absolute robbery."
RB-022,Random Hyperfocus,Warm Deflect,Medium,"Currently falling down a rabbit hole about [insert topic], but wanted to pop up and say I love you both! xx"
RB-023,Random Hyperfocus,Warm Deflect,Low,"Saw this and thought of you: [insert link] xx"
RB-024,Random Hyperfocus,Warm Deflect,Low,"How are you both going? Are you back in [insert location] yet?"
RB-025,Photo and Media Deflects,Warm Deflect,Zero,"Look at this! [Insert photo] (Also hi, sorry for being quiet, love you xx)"
RB-026,Photo and Media Deflects,Warm Deflect,Zero,"[Insert photo] Found this and thought of you guys."
RB-027,Photo and Media Deflects,Warm Deflect,Zero,"[Insert photo of pet/food/view] Proof of life! Sending love xx"
RB-028,Partner and Sister Mentions,Safe Update,Medium,"Lucy says hi! We are just doing [insert boring activity]. Hope you guys are having a good evening xx"
RB-029,Partner and Sister Mentions,Safe Update,Medium,"Saw Shilpa's message, going to try and reply to her tomorrow when my brain is working a bit better. Love you guys xx"
RB-030,Partner and Sister Mentions,Safe Update,Medium,"Lucy and I are just watching a movie, but wanted to send a quick text to say hi and love you! xx"
RB-031,Travel and Logistics,Pure Logistics,Zero,"Landed! xx"
RB-032,Travel and Logistics,Pure Logistics,Low,"My Uber driver asked me to cancel whilst I'm in the car... Just in case he's a psychopath 🙈 [share live location]"
RB-033,Travel and Logistics,Pure Logistics,Low,"Taking Lucy to airport. Nearly there, then coming to you. Will confirm ETA soon."
RB-034,Travel and Logistics,Pure Logistics,Low,"I'm on my way. See my trip progress and arrival time on Maps: [insert link]"
RB-035,The Classic Reset,Honest Reset,Medium,"Parents. Sorry I've been so quiet. Nothing dramatic has happened, I've just been in a bit of a rut. No real news to report but I'm okay. Think about you both a lot. Love you xx"
RB-036,The Classic Reset,Honest Reset,Medium,"Hi. I know it's been a while. Brain's been fried and the longer I left it the harder it got to type. Stupid cycle. Love you both xx"
RB-037,The Classic Reset,Honest Reset,Low,"Sorry for the silence. I've been pretty low and haven't had much to say. But I miss you and wanted you to know I'm okay. Will call soon. Love you xx"
RB-038,The Classic Reset,Honest Reset,Low,"Hi parents. I'm not ignoring you, I promise. Just been in my head a lot lately. Slight disaster of a few weeks tbh 🙈 Love you xx"
RB-039,The Classic Reset,Honest Reset,Medium,"I know we haven't spoken properly in ages. I keep meaning to call and then the day disappears. Zero updates from me but lots of love. Let's try this weekend? xx"
RB-040,Time Blindness and Glitches,Acknowledge Delay,Low,"I saw this message arrive and then it was somehow three weeks later. I am genuinely not sure what happened. Love you both xx"
RB-041,Time Blindness and Glitches,Acknowledge Delay,Low,"January somehow became [current month]. No idea how. Sending love before more time evaporates xx"
RB-042,Time Blindness and Glitches,Acknowledge Delay,Medium,"Mum, Dad — I have been replying to this in my head for approximately forever. It turns out that doesn't count. Sorry! Love you xx"
RB-043,Time Blindness and Glitches,Acknowledge Delay,Low,"Time is genuinely not real. I blinked and two weeks were gone. Still here, still love you xx"
RB-044,Time Blindness and Glitches,Acknowledge Delay,Medium,"My brain said 'reply tomorrow' and then tomorrow was last month apparently. Classic. Hope you're both well xx"
RB-045,Minimal Alive Signals,Buy Time / Reassure,Zero,"Hi. Still here. Love you xx"
RB-046,Minimal Alive Signals,Buy Time / Reassure,Zero,"Not in a talking place right now but didn't want you to worry. Am okay. Love you both xx"
RB-047,Minimal Alive Signals,Buy Time / Reassure,Zero,"Quick wave from Melbourne 👋 Love you xx"
RB-048,Minimal Alive Signals,Buy Time / Reassure,Zero,"Sending love. Will be a better correspondent soon I promise xx"
RB-049,Minimal Alive Signals,Buy Time / Reassure,Zero,"Can't really talk today but wanted you to know I'm thinking of you. Love you xx"
RB-050,Missed Call Recovery,Reset Connection,Low,"Sorry I missed your call. Completely zoned out. Will try you tomorrow morning your time? Love you xx"
RB-051,Missed Call Recovery,Reset Connection,Low,"Missed your call — sorry! Was in the middle of something and then totally forgot. Tomorrow? Love you both xx"
RB-052,Missed Call Recovery,Reset Connection,Low,"Ugh sorry I missed that. Phone was on silent and then it was 11pm. Will actually call tomorrow I promise xx"
RB-053,Missed Call Recovery,Reset Connection,Medium,"Sorry I didn't pick up. Was having a slight disaster of an evening 🙈 Can we reschedule? What time works for you? xx"
RB-054,Admin and Life Disasters,Explain Stressor,Low,"Slight disaster re: [insert thing]. Not life threatening but deeply annoying. Will explain properly when I call. Love you xx"
RB-055,Admin and Life Disasters,Explain Stressor,Medium,"Classic me — [insert minor disaster]. Spent the whole day sorting it out. Brain is completely fried. How are you both doing? xx"
RB-056,Admin and Life Disasters,Explain Stressor,Low,"The flat situation is a slight disaster right now but it's being handled. Will update you properly soon. Love you xx"
RB-057,Admin and Life Disasters,Explain Stressor,Medium,"Total disaster re: [insert admin thing]. I genuinely don't know how I manage to make simple things so complicated 🙈 Love you both xx"
RB-058,Random Hyperfocus,Warm Deflect,Medium,"Dad, completely random but — do you remember [insert memory/question]? For some reason my brain decided it needed to know right now"
RB-059,Random Hyperfocus,Warm Deflect,Medium,"Mum I just read something insane about [insert topic]. Sending it to you. How are you?? xx"
RB-060,Random Hyperfocus,Warm Deflect,Low,"I went down a rabbit hole about flights and looked up how much it would cost to come in [month]. Just casually. For fun. How are you? xx"
RB-061,Random Hyperfocus,Warm Deflect,Medium,"For literally no reason I have been researching [insert thing] for the past two hours. Thought you might find this interesting: [link] xx"
RB-062,Photo and Media Deflects,Warm Deflect,Zero,"[photo] This felt very you, Mum. Hi by the way 👋 Love you xx"
RB-063,Photo and Media Deflects,Warm Deflect,Zero,"[photo] Saw this and immediately thought of Dad. Love you both xx"
RB-064,Photo and Media Deflects,Warm Deflect,Low,"[photo] Melbourne being weird today. Anyway. Hi! Miss you both xx"
RB-065,Photo and Media Deflects,Warm Deflect,Low,"[photo/video] Look at this absolute chaos. Anyway that's my update. Love you guys xx"
RB-066,Partner and Sister Mentions,Safe Update,Medium,"Lucy and I just got back from [insert activity]. She says hi! Hope you're both having a good week xx"
RB-067,Partner and Sister Mentions,Safe Update,Medium,"Shilpa sent me a lovely message. It was really good to hear from her. I'll reply to her properly this week. Love you all xx"
RB-068,Partner and Sister Mentions,Safe Update,Low,"Lucy's making dinner so I have a spare five minutes. Thought I'd pop up and say hi. Miss you both xx"
RB-069,Partner and Sister Mentions,Safe Update,Medium,"We had a really nice weekend, nothing exciting, just a good reset. Lucy says hi to you both. Love you xx"
RB-070,Travel and Logistics,Pure Logistics,Zero,"On the plane. See you soon 🙂 xx"
RB-071,Travel and Logistics,Pure Logistics,Low,"Just landed in [city]. Bit tired but all good. Will message when I'm through baggage. Love you xx"
RB-072,Travel and Logistics,Pure Logistics,Low,"At the gate. Flight looks on time. Will call once I'm settled. Love you both xx"
RB-073,Travel and Logistics,Pure Logistics,Medium,"Flight was fine. Got home. Completely wiped out but wanted to let you know I'm back safe before I pass out 🙈 Love you xx"
RB-074,Medical or Sleep Updates,Low-key Health Check-in,Zero,"Meds being a slight disaster this week. Bit foggy. Nothing dramatic, just wanted to explain the silence. Love you xx"
RB-075,Medical or Sleep Updates,Low-key Health Check-in,Low,"Sleep has been terrible lately which is not helping anything. Am working on it. How are you both doing? xx"
RB-076,Medical or Sleep Updates,Low-key Health Check-in,Low,"Had a GP appointment today — nothing serious, just the usual medication review stuff. It's fine. Love you xx"
RB-077,Medical or Sleep Updates,Low-key Health Check-in,Zero,"Really tired today. Not a bad day just a slow one. Sending love from the sofa 🙈 xx"
```

---

## TONE LINTER RULES

Apply to every generated draft before returning. Flag (do not block) any draft that contains:

```
SHAME CASCADE markers (flag as TONE_WARNING):
- "I'm so sorry" appearing more than once
- "I'm the worst"
- "haven't achieved"
- "I know I always"
- "I'm such a bad [daughter/son/child/person]"

UNVERIFIED PROMISE markers (flag as PROMISE_WARNING):
- Any specific day + time commitment e.g. "I'll call Sunday at 7pm"
- Any "I promise I will [do X] on [day]"
- Note: vague intentions are fine e.g. "will call soon", "talk this weekend?"

FORMAT:
Return flags as part of the JSON response, not as blocked output.
A flagged draft still appears in the digest. The operator decides.
```

---

## DRAFTER SYSTEM PROMPT

Use this exact system prompt for every Gemini API call:

```
You are a drafting assistant for a neurodivergent adult in Melbourne who loves their parents deeply but experiences communication paralysis.

Your job: given an inbound iMessage from a family member, produce two reply drafts in the operator's voice.

STEP 1 — CLASSIFY THE INBOUND:
Classify as: emotional | operational | mixed
If operational: extract the specific ask (money account, document request, logistics question, etc.)

STEP 2 — SELECT A REPLY BRIDGE TEMPLATE:
From the 77 templates provided, select the best match based on:
- inbound classification
- days since last reply (silence duration)
- time of day in Melbourne

Prefer templates in this priority order:
1. Exact category match (e.g. Missed Call Recovery if a call was missed)
2. Energy-appropriate match (Zero if silence > 21 days, Low if 7-21 days, Medium if < 7 days)
3. Freeform generation (last resort only)

STEP 3 — ADAPT THE TEMPLATE:
Fill [insert X] placeholders using inbound context where available.
Mark unfillable placeholders as [FILL IN].
Do not invent facts.

STEP 4 — GENERATE ALTERNATIVE:
Produce a second variant from a different template category or different energy level.

STEP 5 — APPLY VOICE RULES:
Check both drafts against all 11 voice rules.
Check both drafts against tone linter rules.

STEP 6 — RETURN JSON:
{
  "inbound_classification": "emotional|operational|mixed",
  "operational_ask": "string or null",
  "silence_days": number,
  "template_used_primary": "RB-XXX or freeform",
  "template_used_alternative": "RB-XXX or freeform",
  "primary": "draft text",
  "alternative": "draft text",
  "tone_warnings": ["list of warnings or empty"],
  "promise_warnings": ["list of warnings or empty"],
  "confidence": "high|medium|low",
  "confidence_reason": "one sentence"
}

Return only valid JSON. No preamble. No markdown fences.
```

---

## REDACTOR RULES

Strip the following before any text is passed to the Gemini API:

```python
REDACTION_MAP = {
    "Molly Dougall": "MUM",
    "molly.dougall@icloud.com": "MUM_HANDLE",
    "Arvind Dougall": "DAD",
    "Daddy Dougall": "DAD",
    "drarvindougall@gmail.com": "DAD_HANDLE",
    "jonas.dougall@icloud.com": "OPERATOR_HANDLE",
    "Lucy": "PARTNER",
    "Shilpa": "SIBLING",
    "Lokky": "SIBLING_CHILD_1",
    "Layla": "SIBLING_CHILD_2",
}
# Also strip: phone numbers, postcodes, street addresses, policy numbers
# Pattern: UK postcodes [A-Z]{1,2}[0-9][0-9A-Z]? [0-9][A-Z]{2}
# Pattern: phone numbers \+?[\d\s\-\(\)]{10,}
# Pattern: policy numbers [A-Z]\d{8,}
# After redaction, restore family role tokens (MUM → Mum) in the draft output
```

---

## REPO STRUCTURE

Build exactly this structure. No extra files. No stubs.

```
commshubproject/
├── README.md
├── .env.example
├── requirements.txt
├── config/
│   ├── allow_list.yaml
│   ├── voice_rules.md
│   ├── exemplars.json
│   └── digest_schedule.yaml
├── src/
│   ├── __init__.py
│   ├── watcher.py         # reads chat.db, detects new inbounds
│   ├── redactor.py        # strips PII before API call
│   ├── drafter.py         # calls Gemini API, returns structured JSON
│   ├── linter.py          # tone-check and promise-check
│   ├── digest.py          # builds and displays digest in terminal
│   ├── sender.py          # AppleScript iMessage send
│   ├── tracker.py         # SQLite state: inbounds, drafts, sent, skips
│   └── cli.py             # entry points: watch, digest, send, skip
├── launchd/
│   ├── com.commshub.watcher.plist   # hourly poll
│   └── com.commshub.digest.plist    # 4x daily digest
├── scripts/
│   ├── install.sh         # full install: venv, deps, launchd load, FDA prompt
│   └── fda_check.sh       # verify Full Disk Access before running
└── tests/
    ├── test_watcher.py
    ├── test_redactor.py
    ├── test_drafter.py     # uses mock Gemini response
    ├── test_linter.py
    └── test_acceptance.py  # full M1 acceptance scenario
```

---

## FUNCTIONAL REQUIREMENTS — MILESTONE 1

### watcher.py
- Connect to `~/Library/Messages/chat.db` (read-only)
- Query messages table for new rows from allow-listed handles since last poll timestamp
- Filter: sender handle must match allow_list exactly
- Skip: messages where `is_from_me = 1`
- Skip: messages where `cache_has_attachments = 1` AND `text IS NULL` (media-only; log as "media message" without drafting)
- Write new inbounds to tracker with status `pending`
- Store last poll timestamp in tracker

### redactor.py
- Apply REDACTION_MAP (exact string match, case-sensitive)
- Apply regex patterns for phone numbers, postcodes, policy numbers
- Return: `{redacted_text: str, redaction_log: list}`
- Never log original text to disk

### drafter.py
- Load: all 77 Reply Bridge templates, 5 voice exemplars, voice rules, family map
- Load: operator timezone, current Melbourne time, silence duration for this contact
- Build system prompt from DRAFTER SYSTEM PROMPT above
- Call Gemini API with: system prompt + redacted inbound text
- Parse JSON response
- Pass drafts through linter.py
- Write draft to tracker with status `drafted`
- Return full draft object

### linter.py
- Apply SHAME CASCADE checks
- Apply UNVERIFIED PROMISE checks
- Return: `{tone_warnings: list, promise_warnings: list}`
- Never block a draft; only flag

### digest.py
- Run at scheduled times (09:00, 13:00, 18:00, 21:00 Melbourne)
- Query tracker for all items with status `pending` or `drafted`
- Sort: operational items with ask_age > 72h first, then by contact, then by message age
- Render in terminal:

```
╔══════════════════════════════════════════╗
║  COMMS HUB DIGEST — 09:00 Sunday        ║
║  3 items pending                         ║
╚══════════════════════════════════════════╝

━━━ MUM · 11 days ago · OPERATIONAL ━━━
Inbound: [redacted preview, 80 chars max]
⚠️  Stale operational ask: 11 days

[1] PRIMARY (RB-008 · Zero energy)
    Hi — am ok, just very in my head lately. Love you both xx

[2] ALTERNATIVE (RB-045 · Zero energy)
    Hi. Still here. Love you xx

> send 1 | send 2 | edit | skip [reason]

━━━ DAD · 3 days ago · EMOTIONAL ━━━
...
```

- Accept keyboard input: `send 1`, `send 2`, `edit`, `skip`, `skip [reason]`
- On `send N`: call sender.py, update tracker status to `sent`, log timestamp
- On `edit`: open $EDITOR with draft pre-filled, on save call sender.py
- On `skip`: update tracker status to `skipped`, log optional reason

### sender.py
- Receive: `{handle: str, body: str, approval_token: str}`
- Validate approval_token (issued by digest.py, single-use)
- Send via AppleScript:
```applescript
tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "{HANDLE}" of targetService
  send "{BODY}" to targetBuddy
end tell
```
- Return: `{success: bool, timestamp: str, error: str or null}`
- Log send to tracker regardless of success/failure

### tracker.py
- SQLite database at `~/.commshub/state.db`
- Encrypted at rest using sqlcipher or python-pysqlcipher3
- Tables:
  - `inbounds`: id, contact, handle, body_redacted, received_at, status, polled_at
  - `drafts`: id, inbound_id, primary_draft, alternative_draft, template_primary, template_alternative, tone_warnings, promise_warnings, created_at
  - `sent`: id, draft_id, body_sent, sent_at, channel, success
  - `skips`: id, inbound_id, skipped_at, reason
  - `edit_deltas`: id, draft_id, original, edited, sent_at

### cli.py
Entry points:
- `commshub watch` — run one poll cycle manually
- `commshub digest` — display current digest immediately (override schedule)
- `commshub status` — show pending count, last poll time, last digest time
- `commshub stop` — unload launchd agents

---

## LAUNCHD PLISTS

### com.commshub.watcher.plist
- Label: `com.commshub.watcher`
- ProgramArguments: `["/Users/okgoogle13/Projects/commshubproject/venv/bin/python", "-m", "src.cli", "watch"]`
- StartCalendarInterval: every hour at minute 0
- WorkingDirectory: `/Users/okgoogle13/Projects/commshubproject`
- EnvironmentVariables: load from `.env`
- StandardOutPath: `~/.commshub/logs/watcher.log`
- StandardErrorPath: `~/.commshub/logs/watcher.err`

### com.commshub.digest.plist
- Label: `com.commshub.digest`
- ProgramArguments: same pattern, `digest` subcommand
- StartCalendarInterval: 09:00, 13:00, 18:00, 21:00
- Same paths

---

## INSTALL SCRIPT

`install.sh` must:
1. Check macOS version >= 14
2. Check Python >= 3.10
3. Create virtualenv at `./venv`
4. Install requirements
5. Create `~/.commshub/` directory structure
6. Run `fda_check.sh` and pause if FDA not granted
7. Copy launchd plists to `~/Library/LaunchAgents/`
8. Run `launchctl load` for both plists
9. Print first-run instructions including: set GEMINI_API_KEY in `.env`, run `commshub status`

`fda_check.sh` must:
1. Attempt to read one row from `~/Library/Messages/chat.db`
2. If permission denied: print instructions to grant Full Disk Access to Terminal in System Settings → Privacy & Security → Full Disk Access
3. Exit 1 if not granted, exit 0 if granted

---

## ACCEPTANCE TEST

`tests/test_acceptance.py` must simulate this exact scenario:

1. Insert a synthetic inbound row into a test copy of chat.db simulating Mum sending: "Nishu, haven't spoken for two weeks, how are you?"
2. Run watcher — verify row appears in tracker with status `pending`
3. Run redactor on the inbound text — verify "Mum" token appears, no real names in output
4. Run drafter with mocked Gemini response — verify draft appears in tracker with status `drafted`
5. Run linter — verify no false positives on a clean draft
6. Run digest — verify item appears in terminal output with correct format
7. Simulate `send 1` — verify AppleScript would be called with correct handle and body (mock the actual send)
8. Verify tracker shows status `sent` with timestamp

Test must pass with `pytest tests/test_acceptance.py` before Milestone 1 is considered complete.

---

## REQUIREMENTS.TXT

```
google-generativeai>=0.8.0
pysqlcipher3>=1.0.3
pyyaml>=6.0
pytz>=2024.1
pytest>=8.0
python-dotenv>=1.0
```

---

## WHAT TO DO NEXT

1. Scaffold the full repo structure above.
2. Implement every file completely. No TODOs. No stubs. No placeholder functions.
3. Run the acceptance test. Fix until it passes.
4. Output a summary of: files created, any assumptions made, any open questions from the spec that required a decision.
5. Stop. Do not begin Milestone 2.

---

## SUCCESS DEFINITION

The operator runs `commshub digest` at 09:00, sees a drafted reply to Mum's pending message from 11 days ago, types `send 1`, and the message is delivered via iMessage. No copy-paste. No app-switching. Total interaction time under 10 seconds.

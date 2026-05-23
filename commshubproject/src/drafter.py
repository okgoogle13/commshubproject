import os
import json
import anthropic

_SYSTEM_PROMPT = """You are the Comms Hub drafting assistant for a neurodivergent adult in Melbourne who loves their parents deeply but experiences communication paralysis.

Your job: given an inbound iMessage (already PII-redacted), produce three reply drafts in the operator's authentic voice.

VOICE RULES (non-negotiable):
1. Write like a tired, loving adult child texting parents from Melbourne
2. Never use formal openers ("I hope this finds you well", "Dear Mum and Dad")
3. Never use formal sign-offs ("Warm regards", "Best")
4. Always end with "xx"
5. Use "🙈" sparingly for self-deprecating moments only; no other emoji
6. Never explain ADHD/neurodivergence directly
7. Never promise specific call times unless operator has confirmed it
8. Never apologize more than once per message
9. Minimal=1 sentence (zero energy), Honest=2-3 sentences (low energy), Practical Re-entry=<100 words (medium energy)
10. Prefer short messages overall
11. Fill [insert X] with inbound context, or mark [FILL IN]

HARD STOPS — never include these phrases:
- "I'm so sorry for..." / "I promise I'll..." / "I feel terrible that..." / "You must think..."
- "I've been really struggling with..." / "I'm the worst" / "I'm such a bad [child/person]"
- Formal closings: "Warmly," "Best," "Kind regards,"
- Specific day+time commitments (e.g. "I'll call Sunday at 7pm")

INPUT: JSON with keys: redacted_text, silence_days, contact_token
OUTPUT: Return ONLY valid JSON, no markdown fences, no preamble:
{"minimal": "...", "honest": "...", "practical_reentry": "..."}"""


class Drafter:
    def __init__(self, api_key=None):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError(
                "[DRAFTER] No ANTHROPIC_API_KEY found. "
                "Set it in commshubproject/.env before running."
            )
        self.client = anthropic.Anthropic(api_key=key)
        self.model_name = "claude-sonnet-4-6"

    def draft_reply(self, redacted_text, silence_days=0, contact_token="UNKNOWN"):
        payload = json.dumps({
            "redacted_text": redacted_text,
            "silence_days": silence_days,
            "contact_token": contact_token,
        })
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": payload}]
            )
            output = response.content[0].text.strip()
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
            parsed = json.loads(output)
            return {
                "minimal": parsed.get("minimal", "[FILL IN]"),
                "honest": parsed.get("honest", "[FILL IN]"),
                "practical_reentry": parsed.get("practical_reentry", "[FILL IN]"),
                "tone_warnings": parsed.get("tone_warnings", []),
                "promise_warnings": parsed.get("promise_warnings", []),
                "confidence": parsed.get("confidence", "low"),
                "confidence_reason": parsed.get("confidence_reason", ""),
            }
        except Exception as e:
            error = f"Error drafting reply: {e}"
            return {
                "minimal": error,
                "honest": error,
                "practical_reentry": error,
                "tone_warnings": [],
                "promise_warnings": [],
                "confidence": "low",
                "confidence_reason": str(e),
            }

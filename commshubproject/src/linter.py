import re


class Linter:
    def __init__(self):
        self._forbidden_phrases = [
            "I'm so sorry for",
            "I promise I'll",
            "I feel terrible that",
            "You must think",
            "I've been really struggling with",
            "I'm the worst",
            "haven't achieved",
            "I know I always",
            "I'm such a bad",
            "Kind regards",
            "Warmly,",
            "Best,",
        ]
        # Day + specific time: "Sunday at 7pm", "Monday at 8:30am", etc.
        self._day_time_re = re.compile(
            r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
            r".{0,40}"
            r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b",
            re.IGNORECASE,
        )
        # "I promise I will ... on [day]"
        self._promise_day_re = re.compile(
            r"i promise i will .{0,50} on \b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            re.IGNORECASE,
        )

    def check_draft(self, draft_text):
        text = str(draft_text)
        lower = text.lower()
        flags = []

        for phrase in self._forbidden_phrases:
            if phrase.lower() in lower:
                flags.append(phrase)

        if self._day_time_re.search(text):
            flags.append("UNVERIFIED_PROMISE: specific day+time commitment detected")

        if self._promise_day_re.search(text):
            flags.append("UNVERIFIED_PROMISE: 'I promise I will ... on [day]' pattern")

        return {"passed": len(flags) == 0, "flags": flags}

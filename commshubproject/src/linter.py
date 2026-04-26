# ### FILE: commshubproject/src/linter.py
class Linter:
    def __init__(self):
        self.forbidden_patterns = [
            "SHAME CASCADE",
            "UNVERIFIED PROMISE",
            "I'm so sorry",
            "I will absolutely",
            "I promise"
        ]

    def check_draft(self, draft_text):
        flags = []
        lower_draft = draft_text.lower()
        for pattern in self.forbidden_patterns:
            if pattern.lower() in lower_draft:
                flags.append(pattern)
        
        return {
            "passed": len(flags) == 0,
            "flags": flags
        }

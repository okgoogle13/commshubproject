# ### FILE: commshubproject/src/linter.py
class Linter:
    def __init__(self):
        self.forbidden_patterns = [
            "SHAME CASCADE",
            "UNVERIFIED PROMISE",
            "I'm so sorry for",
            "I promise I'll",
            "I feel terrible that",
            "You must think",
            "I've been really struggling with",
            "Warmly",
            "Best",
            "Kind regards"
        ]

    def check_draft(self, draft_text):
        flags = []
        lower_draft = str(draft_text).lower()
        for pattern in self.forbidden_patterns:
            if pattern.lower() in lower_draft:
                flags.append(pattern)
        
        return {
            "passed": len(flags) == 0,
            "flags": flags
        }

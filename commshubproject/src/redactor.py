# ### FILE: commshubproject/src/redactor.py
import re

class Redactor:
    def __init__(self):
        self.redaction_map = {
            "Mum": "[REDACTED_MUM]",
            "Dad": "[REDACTED_DAD]",
            "Partner": "[REDACTED_PARTNER]",
            "Sibling": "[REDACTED_SIBLING]",
            "Operator": "[REDACTED_OPERATOR]"
        }
        self.phone_regex = re.compile(r'\+?\d{1,3}[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}')
        self.postcode_regex = re.compile(r'\b[A-PR-UWYZ][A-HK-Y0-9][A-HJKPS-UW0-9]?[A-HJKPS-UW0-9]? ?[0-9][ABD-HJLNP-UW-Z]{2}\b', re.IGNORECASE)

    def redact(self, text):
        if not text:
            return text
            
        redacted_text = text
        for name, placeholder in self.redaction_map.items():
            redacted_text = re.sub(rf'\b{name}\b', placeholder, redacted_text, flags=re.IGNORECASE)
            
        redacted_text = self.phone_regex.sub('[REDACTED_PHONE]', redacted_text)
        redacted_text = self.postcode_regex.sub('[REDACTED_POSTCODE]', redacted_text)
        
        return redacted_text

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
        self.phone_regex = re.compile(r'\b04\d{2}\s?\d{3}\s?\d{3}\b')
        self.postcode_regex = re.compile(r'\b\d{4}\b')
        self.address_regex = re.compile(r'\b\d+\s+\w+\s+(St|Rd|Ave|Dr|Cres|Blvd|Ct|Pl|Way|Tce|Pde)\b', re.IGNORECASE)

    def redact(self, text):
        if not text:
            return text
            
        redacted_text = text
        for name, placeholder in self.redaction_map.items():
            redacted_text = re.sub(rf'\b{name}\b', placeholder, redacted_text, flags=re.IGNORECASE)
            
        redacted_text = self.phone_regex.sub('[REDACTED_PHONE]', redacted_text)
        redacted_text = self.postcode_regex.sub('[REDACTED_POSTCODE]', redacted_text)
        redacted_text = self.address_regex.sub('[REDACTED_ADDRESS]', redacted_text)
        
        return redacted_text

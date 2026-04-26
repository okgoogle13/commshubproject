import re
import os
import yaml


class Redactor:
    def __init__(self, allow_list=None):
        if allow_list is None:
            config_path = os.path.join(os.path.dirname(__file__), "../config/allow_list.yaml")
            try:
                with open(config_path) as f:
                    data = yaml.safe_load(f)
                allow_list = data.get("allow_list", [])
            except FileNotFoundError:
                allow_list = []

        # Build name → token map (full name, word parts > 3 chars, aliases)
        self._name_tokens = {}
        self._handle_tokens = {}
        for contact in allow_list:
            full_name = contact["name"]
            token = f"[REDACTED_{contact['token']}]"
            self._name_tokens[full_name] = token
            for word in full_name.split():
                if len(word) > 3:
                    self._name_tokens[word] = token
            for alias in contact.get("aliases", []):
                self._name_tokens[alias] = token
            # Store handle as email token (most natural for downstream)
            self._handle_tokens[contact["imessage_handle"].lower()] = "[REDACTED_EMAIL]"

        self._phone_regex = re.compile(
            r"(\+44\s?7\d{3}\s?\d{6}"    # +44 7xxx xxxxxx
            r"|07\d{9}"                    # 07xxxxxxxxx
            r"|0\d{4}\s?\d{6}"            # 0xxxx xxxxxx
            r"|\b04\d{2}\s?\d{3}\s?\d{3}\b)",  # AU: 04xx xxx xxx
            re.IGNORECASE,
        )
        self._postcode_uk_regex = re.compile(
            r"\b[A-PR-UWYZ][A-HK-Y0-9][A-HJKPS-UW0-9]?[A-HJKPS-UW0-9]?"
            r" ?[0-9][ABD-HJLNP-UW-Z]{2}\b",
            re.IGNORECASE,
        )
        self._postcode_au_regex = re.compile(r"\b\d{4}\b")
        self._address_regex = re.compile(
            r"\b\d+\s+\w+\s+(St|Rd|Ave|Dr|Cres|Blvd|Ct|Pl|Way|Tce|Pde)\b",
            re.IGNORECASE,
        )
        self._email_regex = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        )

    def redact(self, text):
        if not text:
            return text
        result = text

        # iMessage handles (exact, case-insensitive)
        for handle, token in self._handle_tokens.items():
            result = re.sub(re.escape(handle), token, result, flags=re.IGNORECASE)

        # Emails before names (handles like molly@icloud.com would otherwise survive)
        result = self._email_regex.sub("[REDACTED_EMAIL]", result)

        # Full names / first names
        for name, token in self._name_tokens.items():
            result = re.sub(rf"\b{re.escape(name)}\b", token, result, flags=re.IGNORECASE)

        result = self._phone_regex.sub("[REDACTED_PHONE]", result)
        result = self._postcode_uk_regex.sub("[REDACTED_POSTCODE]", result)
        result = self._postcode_au_regex.sub("[REDACTED_POSTCODE]", result)
        result = self._address_regex.sub("[REDACTED_ADDRESS]", result)

        return result

# ### FILE: commshubproject/src/digest.py
import yaml
from datetime import datetime

class DigestGenerator:
    def __init__(self, schedule_path="config/digest_schedule.yaml"):
        self.schedule_path = schedule_path

    def load_schedule(self):
        try:
            with open(self.schedule_path, "r") as f:
                data = yaml.safe_load(f)
                return data.get("digest_times", [])
        except FileNotFoundError:
            return []

    def generate_digest(self, messages):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        digest = f"--- COMMS HUB DIGEST ({timestamp}) ---\n"
        for idx, msg in enumerate(messages, 1):
            digest += f"{idx}. {msg}\n"
        digest += "--------------------------------------\n"
        return digest

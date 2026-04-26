# ### FILE: commshubproject/src/drafter.py
import os
import json
import google.generativeai as genai

class Drafter:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-pro-preview')

    def load_rules(self):
        try:
            with open("config/voice_rules.md", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Be concise, professional but warm."

    def draft_reply(self, message_text):
        rules = self.load_rules()
        prompt = (
            f"Draft a short iMessage reply to the following text.\n"
            f"Adhere strictly to these Voice Rules:\n{rules}\n\n"
            f"Return ONLY valid JSON format with a 'draft' key.\n\n"
            f"Message: {message_text}"
        )
        try:
            response = self.model.generate_content(prompt)
            output = response.text
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            draft_json = json.loads(output)
            return draft_json.get("draft", "Error: No draft generated.")
        except Exception as e:
            return f"Error drafting reply: {str(e)}"

# ### FILE: commshubproject/src/drafter.py
import os
import json
import yaml
import google.generativeai as genai

class Drafter:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def load_rules(self):
        try:
            with open("config/voice_rules.md", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "- Be concise, professional but warm."

    def draft_reply(self, message_text, persona="default"):
        rules = self.load_rules()
        prompt = (
            f"You are the Comms Hub drafting assistant. Follow the Voice Rules exactly.\n\n"
            f"Given the inbound message below, produce three reply drafts: minimal, honest, and practical_reentry.\n\n"
            f"Voice Rules:\n{rules}\n\n"
            f"Inbound message: {message_text}\n\n"
            f"Return ONLY valid JSON with exactly these keys: \"minimal\", \"honest\", \"practical_reentry\".\n"
            f"No extra text, no markdown fences."
        )
        try:
            response = self.model.generate_content(prompt)
            output = response.text
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
                
            draft_json = json.loads(output)
            return {
                "minimal": draft_json.get("minimal", "Error generating minimal draft"),
                "honest": draft_json.get("honest", "Error generating honest draft"),
                "practical_reentry": draft_json.get("practical_reentry", "Error generating practical_reentry draft")
            }
        except Exception as e:
            return {
                "minimal": f"Error drafting reply: {str(e)}",
                "honest": f"Error drafting reply: {str(e)}",
                "practical_reentry": f"Error drafting reply: {str(e)}"
            }

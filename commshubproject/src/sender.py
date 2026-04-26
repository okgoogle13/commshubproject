# ### FILE: commshubproject/src/sender.py
from macpymessenger import ScriptManager

class Sender:
    def __init__(self):
        self.manager = ScriptManager()

    def send_message(self, phone_number, message_body):
        try:
            self.manager.send_message(phone_number, message_body)
            return True
        except Exception as e:
            print(f"Failed to send message to {phone_number}: {e}")
            return False

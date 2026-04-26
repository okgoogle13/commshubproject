import time


class Sender:
    def __init__(self, tracker=None):
        self.tracker = tracker
        self._valid_tokens = set()

    def issue_token(self, message_id):
        token = f"tok_{message_id}_{int(time.time())}"
        self._valid_tokens.add(token)
        return token

    def consume_token(self, token):
        if token in self._valid_tokens:
            self._valid_tokens.discard(token)
            return True
        return False

    def send_message(self, imessage_handle, body, message_id, draft_mode, approval_token):
        if not self.consume_token(approval_token):
            raise PermissionError(f"Invalid or already-used approval token: {approval_token}")
        try:
            from macpymessenger import ScriptManager
            sm = ScriptManager()
            sm.send_message_to_email(imessage_handle, body)
        except Exception as e:
            print(f"[SENDER] AppleScript error: {e}")
            return False
        sent_at = str(time.time())
        if self.tracker:
            self.tracker.mark_sent(message_id, draft_mode, body, sent_at)
        print(f"[SENDER] Sent '{body[:40]}...' to {imessage_handle}")
        return True

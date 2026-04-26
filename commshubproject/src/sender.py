import time
import subprocess


def _send_via_applescript(handle, body):
    """Send an iMessage using osascript directly — no macpymessenger dependency."""
    script = f'''
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "{handle}" of targetService
    send "{body}" to targetBuddy
end tell
'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")


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
            _send_via_applescript(imessage_handle, body)
        except Exception as e:
            print(f"[SENDER] Error sending message: {e}")
            return False
        sent_at = str(time.time())
        if self.tracker:
            self.tracker.mark_sent(message_id, draft_mode, body, sent_at)
        print(f"[SENDER] Sent to {imessage_handle}: {body[:50]}")
        return True

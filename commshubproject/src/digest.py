import os
import time
import tempfile
import subprocess


def sort_pending_items(items):
    now = time.time()

    def _key(item):
        age_days = (now - (item.get("received_at") or 0)) / 86400
        is_old_operational = 1 if age_days > 72 else 0
        return (-is_old_operational, -age_days)

    return sorted(items, key=_key)


class Digest:
    def __init__(self, tracker=None, sender=None):
        self.tracker = tracker
        self.sender = sender

    def format_item(self, item):
        now = time.time()
        age_days = int((now - (item.get("received_at") or 0)) / 86400)
        contact = item.get("contact_token", "UNKNOWN")
        preview = (item.get("redacted_text") or "")[:80]
        lines = [
            "",
            "=" * 60,
            f"From: {contact}  |  {age_days} day(s) ago",
            f"Msg:  {preview}",
        ]
        if item.get("draft_minimal"):
            lines += [
                "",
                f"  [1] Minimal:   {item['draft_minimal']}",
                f"  [2] Honest:    {item['draft_honest']}",
                f"  [3] Practical: {item['draft_practical']}",
                "",
                "  Commands: send 1 | send 2 | send 3 | edit | skip | skip [reason]",
            ]
        else:
            lines += [
                "",
                "  !! DRAFT UNAVAILABLE",
                "  Commands: edit | skip | skip [reason]",
            ]
        return "\n".join(lines)

    def _open_editor(self, initial_text):
        editor = os.environ.get("EDITOR", "nano")
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write(initial_text)
            fname = f.name
        subprocess.call([editor, fname])
        with open(fname) as f:
            edited = f.read().strip()
        os.unlink(fname)
        return edited

    def run_interactive(self):
        if not self.tracker:
            print("[DIGEST] No tracker configured.")
            return
        items = sort_pending_items(self.tracker.get_pending_inbounds())
        if not items:
            print("[DIGEST] No pending items.")
            return
        print(f"\n[DIGEST] {len(items)} pending item(s)")
        for item in items:
            print(self.format_item(item))
            while True:
                try:
                    cmd = input("> ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n[DIGEST] Interrupted.")
                    return
                if cmd in ("send 1", "send 2", "send 3"):
                    mode_map = {
                        "send 1": ("minimal", "draft_minimal"),
                        "send 2": ("honest", "draft_honest"),
                        "send 3": ("practical", "draft_practical"),
                    }
                    mode, key = mode_map[cmd]
                    draft_text = item.get(key)
                    if not draft_text:
                        print("[DIGEST] No draft for that option.")
                        continue
                    if self.sender:
                        token = self.sender.issue_token(item["message_id"])
                        success = self.sender.send_message(
                            item.get("imessage_handle", ""),
                            draft_text,
                            item["message_id"],
                            mode,
                            token,
                        )
                        if success:
                            print("[DIGEST] Sent. Moving to next item.")
                    break
                elif cmd == "edit":
                    initial = item.get("draft_minimal") or ""
                    edited = self._open_editor(initial)
                    if edited and self.sender:
                        confirm = input(f"Send this edit? (y/n)\n  {edited[:80]}\n> ").strip().lower()
                        if confirm == "y":
                            token = self.sender.issue_token(item["message_id"])
                            self.sender.send_message(
                                item.get("imessage_handle", ""),
                                edited,
                                item["message_id"],
                                "edited",
                                token,
                            )
                    break
                elif cmd.startswith("skip"):
                    reason = cmd[4:].strip() or None
                    if self.tracker:
                        self.tracker.mark_skipped(item["message_id"], reason=reason)
                    print("[DIGEST] Skipped.")
                    break
                else:
                    print("Unknown command. Try: send 1 | send 2 | send 3 | edit | skip")

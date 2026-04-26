import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.commshub/.env"))
load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Comms Hub — family message assistant")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("watch", help="Run one watcher poll cycle")
    subparsers.add_parser("digest", help="Run interactive digest immediately")
    subparsers.add_parser("status", help="Show pending count and last poll time")
    subparsers.add_parser("stop", help="Unload launchd agents")

    # Legacy flags
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--test-draft", type=str)
    parser.add_argument("--send", type=str)
    parser.add_argument("--body", type=str)

    args = parser.parse_args()

    if args.command == "watch" or args.fetch:
        _run_watch()
    elif args.command == "digest":
        _run_digest()
    elif args.command == "status":
        _run_status()
    elif args.command == "stop":
        _run_stop()
    elif args.test_draft:
        _run_test_draft(args.test_draft)
    elif args.send and args.body:
        print("[CLI] Direct send is removed. Use 'commshub digest' to send.")
    else:
        parser.print_help()


def _get_tracker():
    from src.tracker import Tracker
    return Tracker()


def _run_watch():
    import time
    from src.watcher import Watcher
    from src.redactor import Redactor
    from src.drafter import Drafter
    from src.tracker import Tracker

    tracker = _get_tracker()
    watcher = Watcher()
    redactor = Redactor()
    drafter = Drafter()

    print("[WATCH] Polling chat.db...")
    messages = watcher.fetch_and_filter()
    print(f"[WATCH] {len(messages)} new inbound(s) from allow-listed contacts.")

    for msg in messages:
        if tracker.is_known_message(msg["id"]):
            continue
        safe_text = redactor.redact(msg["message"])
        silence = tracker.days_since_last_sent(msg["contact_token"])
        tracker.record_inbound(
            message_id=msg["id"],
            contact_token=msg["contact_token"],
            imessage_handle=msg["handle"],
            redacted_text=safe_text,
            received_at=int(time.time()),
        )
        print(f"[WATCH] Drafting for {msg['contact_token']} (silence: {int(silence)}d)...")
        drafts = drafter.draft_reply(safe_text, silence_days=int(silence), contact_token=msg["contact_token"])
        tracker.record_draft(
            message_id=msg["id"],
            draft_minimal=drafts["minimal"],
            draft_honest=drafts["honest"],
            draft_practical=drafts["practical_reentry"],
            template_minimal="freeform",
            template_honest="freeform",
            template_practical="freeform",
        )
        print(f"[WATCH] Draft ready for {msg['contact_token']}.")

    tracker.set_last_poll(str(int(time.time())))
    print("[WATCH] Poll complete.")


def _run_digest():
    from src.digest import Digest
    from src.sender import Sender

    tracker = _get_tracker()
    sender = Sender(tracker=tracker)
    digest = Digest(tracker=tracker, sender=sender)
    digest.run_interactive()


def _run_status():
    tracker = _get_tracker()
    s = tracker.get_status_summary()
    print(f"[STATUS] Pending: {s['pending']} | Sent: {s['total_sent']} | Last poll: {s['last_poll']}")


def _run_stop():
    import subprocess
    for agent in ("com.commshub.watcher", "com.commshub.digest"):
        plist = os.path.expanduser(f"~/Library/LaunchAgents/{agent}.plist")
        result = subprocess.run(["launchctl", "unload", plist], capture_output=True)
        status = "Unloaded" if result.returncode == 0 else f"Error: {result.stderr.decode().strip()}"
        print(f"[STOP] {agent}: {status}")


def _run_test_draft(snippet):
    from src.redactor import Redactor
    from src.drafter import Drafter
    from src.linter import Linter

    redactor = Redactor()
    safe = redactor.redact(snippet)
    print(f"[TEST] Redacted: {safe}")

    drafter = Drafter()
    drafts = drafter.draft_reply(safe, silence_days=7)
    print(f"\n[1] Minimal:   {drafts['minimal']}")
    print(f"[2] Honest:    {drafts['honest']}")
    print(f"[3] Practical: {drafts['practical_reentry']}")

    linter = Linter()
    for mode, key in [("Minimal", "minimal"), ("Honest", "honest"), ("Practical", "practical_reentry")]:
        result = linter.check_draft(drafts[key])
        status = "PASS" if result["passed"] else f"WARN: {result['flags']}"
        print(f"[LINTER] {mode}: {status}")


if __name__ == "__main__":
    main()

# ### FILE: commshubproject/src/cli.py
import argparse
import sys
from dotenv import load_dotenv

from .watcher import Watcher
from .redactor import Redactor
from .drafter import Drafter
from .linter import Linter
from .sender import Sender

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Comms Hub CLI agent.")
    parser.add_argument("--fetch", action="store_true", help="Fetch recent messages from chat.db")
    parser.add_argument("--test-draft", type=str, help="Run a test draft workflow for a given snippet")
    parser.add_argument("--send", type=str, help="Phone number to send a test message to")
    parser.add_argument("--body", type=str, help="Message body for sending")
    
    args = parser.parse_args()
    
    if args.fetch:
        print("Fetching latest messages...")
        watcher = Watcher()
        msgs = watcher.fetch_recent_messages()
        for m in msgs:
            print(m)
            
    if args.test_draft:
        print(f"Original Text: {args.test_draft}")
        
        redactor = Redactor()
        safe_text = redactor.redact(args.test_draft)
        print(f"Redacted Text: {safe_text}")
        
        drafter = Drafter()
        draft = drafter.draft_reply(safe_text)
        print(f"Generated Draft: {draft}")
        
        linter = Linter()
        lint_result = linter.check_draft(draft)
        if lint_result["passed"]:
            print("Linter: PASS")
        else:
            print(f"Linter: FAIL - Flags: {lint_result['flags']}")
            
    if args.send and args.body:
        print(f"Sending message to {args.send}...")
        sender = Sender()
        success = sender.send_message(args.send, args.body)
        if success:
            print("Message sent successfully.")
        else:
            print("Failed to send message.")
            sys.exit(1)

if __name__ == "__main__":
    main()

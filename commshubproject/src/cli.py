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
    parser.add_argument("--persona", type=str, default="default", help="Voice persona style to use")
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
        drafts = drafter.draft_reply(safe_text, persona=args.persona)
        
        print("\nGenerated Drafts:")
        print(f"[1] Minimal: {drafts.get('minimal', '')}")
        print(f"[2] Honest: {drafts.get('honest', '')}")
        print(f"[3] Practical Re-entry: {drafts.get('practical_reentry', '')}")
        
        print("\n[1] Minimal  [2] Honest  [3] Practical Re-entry  [e] Edit manually")
        # In a real CLI we would process input here
        
        linter = Linter()
        # Linting all drafts combined or individually. For simplicity, just run on one or all
        combined_text = f"{drafts.get('minimal')} {drafts.get('honest')} {drafts.get('practical_reentry')}"
        lint_result = linter.check_draft(combined_text)
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

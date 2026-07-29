# ### FILE: commshubproject/src/tracker.py
class Tracker:
    def __init__(self):
        self.processed_ids = set()

    def is_processed(self, msg_id):
        return msg_id in self.processed_ids

    def mark_processed(self, msg_id):
        self.processed_ids.add(msg_id)

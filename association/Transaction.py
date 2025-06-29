

class Transaction:
    def __init__(self, tid, items):
        self.tid = tid
        self.items = set(items)  # store as set for easy support checks

    def __repr__(self): ## <=> toString()
        return f"Transaction(id={self.tid}, items={self.items})"

class NoMatchingReceiverException(Exception):
    def __init__(self, event, *args):
        self.msg = f"no matching receiver for '{event}'"
        super().__init__(*args)

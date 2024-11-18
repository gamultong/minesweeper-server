
class InvalidEventTypeException(BaseException):
    def __init__(self, event, *args):
        self.msg = f"invalid event type: '{event}'"
        super().__init__(*args)
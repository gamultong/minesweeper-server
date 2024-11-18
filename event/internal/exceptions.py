class NoMatchingHandlerException(BaseException):
    def __init__(self, event, *args):
        self.msg = f"no matching handler for '{event}'"
        super().__init__(*args)
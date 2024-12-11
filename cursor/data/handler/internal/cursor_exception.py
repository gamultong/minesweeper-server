from board.data import Point


class AlreadyWatchingException(Exception):
    def __init__(self, watcher: str, watching: str):
        self.msg = f"cursor {watcher} is already watching {watching}"


class NoMatchingCursorException(Exception):
    def __init__(self, cursor_id: str):
        self.msg = f"no matching cursor with id: {cursor_id}"


class NotWatchableException(Exception):
    def __init__(self, p: Point, cursor_id: str):
        self.msg = f"position: ({p.x}, {p.y}) is not watchable to cursor: {cursor_id}"


class NotWatchingException(Exception):
    def __init__(self, watcher: str, watching: str):
        self.msg = f"cursor {watcher} is not watching {watching}"

from board.data import Point
from cursor.data import Cursor, Color
from .cursor_exception import (
    AlreadyWatchingException,
    NoMatchingCursorException,
    NotWatchableException,
    NotWatchingException
)


class CursorHandler:
    cursor_dict: dict[str, Cursor] = {}

    watchers: dict[str, list[str]] = {}
    watching: dict[str, list[str]] = {}

    @staticmethod
    def create_cursor(conn_id: str):
        cursor = Cursor.create(conn_id)

        CursorHandler.cursor_dict[conn_id] = cursor

        return cursor

    @staticmethod
    def remove_cursor(conn_id: str):
        # TODO: 예외 처리?
        if conn_id in CursorHandler.cursor_dict:
            del CursorHandler.cursor_dict[conn_id]

    @staticmethod
    def get_cursor(conn_id: str) -> Cursor | None:
        if conn_id in CursorHandler.cursor_dict:
            return CursorHandler.cursor_dict[conn_id]

    # range 안에 커서가 있는가
    @staticmethod
    def exists_range(start: Point, end: Point, *exclude_ids) -> list[Cursor]:
        result = []
        for key in CursorHandler.cursor_dict:
            if exclude_ids and key in exclude_ids:
                continue
            cur = CursorHandler.cursor_dict[key]
            if start.x > cur.position.x:
                continue
            if end.x < cur.position.x:
                continue
            if start.y < cur.position.y:
                continue
            if end.y > cur.position.y:
                continue
            result.append(cur)

        return result

    # 커서 view에 tile이 포함되는가
    @staticmethod
    def view_includes(p: Point, *exclude_ids) -> list[Cursor]:
        result = []
        for key in CursorHandler.cursor_dict:
            if exclude_ids and key in exclude_ids:
                continue
            cur = CursorHandler.cursor_dict[key]
            if (cur.position.x - cur.width) > p.x:
                continue
            if (cur.position.x + cur.width) < p.x:
                continue
            if (cur.position.y - cur.height) > p.y:
                continue
            if (cur.position.y + cur.height) < p.y:
                continue
            result.append(cur)

        return result

    @staticmethod
    def add_watcher(watcher: Cursor, watching: Cursor) -> None:
        watcher_id = watcher.conn_id
        watching_id = watching.conn_id

        watcher_exists = CursorHandler.check_cursor_exists(watcher_id)
        watching_exists = CursorHandler.check_cursor_exists(watching_id)

        if not (watcher_exists and watching_exists):
            raise NoMatchingCursorException()

        if CursorHandler.check_cursor_watching(watching_id, watcher_id):
            raise AlreadyWatchingException()

        if not watcher.check_in_view(watching.position):
            raise NotWatchableException()

        if not watcher_id in CursorHandler.watching:
            CursorHandler.watching[watcher_id] = []
        CursorHandler.watching[watcher_id].append(watching_id)

        if not watching_id in CursorHandler.watchers:
            CursorHandler.watchers[watching_id] = []
        CursorHandler.watchers[watching_id].append(watcher_id)

    @staticmethod
    def remove_watcher(watcher: Cursor, watching: Cursor):
        watcher_id = watcher.conn_id
        watching_id = watching.conn_id

        watcher_exists = CursorHandler.check_cursor_exists(watcher_id)
        watching_exists = CursorHandler.check_cursor_exists(watching_id)

        if not (watcher_exists and watching_exists):
            raise NoMatchingCursorException()

        if not CursorHandler.check_cursor_watching(watching_id, watcher_id):
            raise NotWatchingException()

        CursorHandler.watching[watcher_id].remove(watching_id)
        if len(CursorHandler.watching[watcher_id]) == 0:
            del CursorHandler.watching[watcher_id]

        CursorHandler.watchers[watching_id].remove(watcher_id)
        if len(CursorHandler.watchers[watching_id]) == 0:
            del CursorHandler.watchers[watching_id]

    @staticmethod
    def get_watchers(cursor_id: str) -> list[str]:
        if not CursorHandler.check_cursor_exists(cursor_id):
            raise NoMatchingCursorException()

        if cursor_id in CursorHandler.watchers:
            return CursorHandler.watchers[cursor_id].copy()

        return []

    @staticmethod
    def get_watching(cursor_id: str) -> list[str]:
        if not CursorHandler.check_cursor_exists(cursor_id):
            raise NoMatchingCursorException()

        if cursor_id in CursorHandler.watching:
            return CursorHandler.watching[cursor_id].copy()

        return []

    @staticmethod
    def check_cursor_exists(id: str):
        return id in CursorHandler.cursor_dict

    @staticmethod
    def check_cursor_watching(watching_id: str, watcher_id: str):
        """
        커서 watching 관계가 형성되어 있으면 True
        """
        watcher_rel = watching_id in CursorHandler.watchers
        watcher_rel = watcher_rel and watcher_id in CursorHandler.watchers[watching_id]

        watching_rel = watcher_id in CursorHandler.watching
        watching_rel = watching_rel and watching_id in CursorHandler.watching[watcher_id]

        return watcher_rel and watching_rel

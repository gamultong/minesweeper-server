from cursor import Cursor
from board import Point

class CursorManager:
    cursor_dict: dict[str, Cursor]

    @staticmethod
    def create(conn_id: str):
        cursor = Cursor.create(conn_id)
        CursorManager.cursor_dict[conn_id] = cursor

    @staticmethod
    def remove(conn_id: str):
        if conn_id in CursorManager.cursor_dict:
            del CursorManager.cursor_dict[conn_id]

    @staticmethod
    def exists_range(start: Point, end: Point) -> list[Cursor]:
        # 일단 broadcast. 추후 고쳐야 함.
        return list(CursorManager.cursor_dict.values())

    @staticmethod
    def view_includes(p: Point) -> list[Cursor]:
        # 일단 broadcast. 추후 고쳐야 함.
        return list(CursorManager.cursor_dict.values())